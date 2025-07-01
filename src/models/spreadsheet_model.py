import sys
import json
from pathlib import Path
from PySide6.QtCore import (
    QAbstractTableModel,
    Qt,
    QUrl,
    QModelIndex,
    Slot,
    Property,
    Signal,
    QSortFilterProxyModel,
    QAbstractListModel,
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QFont, QFontMetrics
import threading
from queue import Queue, Empty
from time import sleep
import asyncio
from qasync import asyncSlot
from asyncio import get_event_loop
from collections import deque
import re
import random
import pickle
from concurrent.futures import ThreadPoolExecutor
import os
from .data_structures import TaskTypes, collectionElement, collection
from .background_tasks import setup_background_tasks
from .image_viewer import show_images

SAVE_FILE = "data/general.json"
MEDIA_ROOT = "data/media"


class RoleTypes:
    NAMES = "names"
    DEPENDENCIES = "dependencies"
    ATTRIBUTES = "attributes"
    PATH = "path"

class collectionElement:
    def __init__(self, rowHeights, columnWidths):
        self.data = [["names"]]
        self.roles = ["names"]
        self.rowHeights = rowHeights
        self.columnWidths = columnWidths

class collection:
    def __init__(self):
        self.collections = {}
        self.checkings_list = []
        self.sortings_list = []
        self.collectionName = ""

class SpreadsheetModel(QAbstractTableModel):
    signal = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.default_width = 100
        self.horizontal_padding = 5
        self.vertical_padding = 5
        self.font = QFont("Arial", 10)

        self.metrics = QFontMetrics(self.font)
        self._rows_nb = 0
        self._columns_nb = 0
        self._errorMsg = ""
        self._verticalScrollPosition = 0
        self._verticalScrollSize = 0
        self._tableViewContentY = 0
        self._tableViewHeight = 0
        self._horizontalScrollPosition = 0
        self._horizontalScrollSize = 0
        self._tableViewContentX = 0
        self._tableViewWidth = 0
        self._data_lock = threading.Lock()
        self.condition = threading.Condition(self._data_lock)
        self.imports_loaded = threading.Event()
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._selected_row = -1
        self._selected_column = -1
        self._role_types = [RoleTypes.NAMES, RoleTypes.DEPENDENCIES, RoleTypes.ATTRIBUTES, RoleTypes.PATH]

        
        if not Path("data").exists():
            Path("data").mkdir(parents=True, exist_ok=True)
        try:
            with open(SAVE_FILE, "rb") as f:
                collections = pickle.load(f)
            if collections:
                self._collections = collections
                self.loadSpreadsheet(collections.collectionName)
        except FileNotFoundError:
            self._collections = collection()
            self.collectionName = self._getDefaultSpreadsheetName()
            self.createCollection(self.collectionName)
        self.collections = self._collections.collections
        self.checkings_list = self._collections.checkings_list
        self.sortings_list = self._collections.sortings_list
        
    def start_background_tasks(self):
        setup_background_tasks(self)
    
    @Slot(result=list)
    def get_role_types(self):
        return self._role_types
     
    @Slot(result=str)
    def get_font_family(self):
        return self.font.family()
    
    @Slot(result=int)
    def get_font_size(self):
        return self.font.pointSize()
    
    @Slot(result=int)
    def get_horizontal_padding(self):
        return self.horizontal_padding

    @Slot(result=int)
    def get_vertical_padding(self):
        return self.vertical_padding

    @Slot(int, result=int)
    def columnWidth(self, column):
        if 0 <= column < (len(self._data[0]) if self._data else 0):
            prevWidth = self._columnWidths[column - 1] if column > 0 else 0
            return self._columnWidths[column] - prevWidth
        return self.default_width + self.horizontal_padding * 2

    @Slot(int, result=int)
    def rowHeight(self, row):
        if 0 <= row < len(self._data):
            prevHeight = self._rowHeights[row - 1] if row > 0 else 0
            return self._rowHeights[row] - prevHeight
        return self.metrics.height() + self.vertical_padding * 2
    
    @Slot(result=str)
    def get_collectionName(self):
        return self.collectionName

    @Slot(result=str)
    def getCollectionName(self):
        """Return the current collection name."""
        return self.collectionName

    def _getDefaultSpreadsheetName(self):
        """Generate a default spreadsheet name not already used."""
        i = 1
        while f"Default_{i}" in self._collections.collections:
            i += 1
        return f"Default_{i}"

    @Slot(str)
    def setSpreadsheetName(self, name):
        with self._data_lock:
            if name in self.collections:
                return
            self.collections[name] = self._collection
            del self.collections[self.collectionName]
            for i, task in enumerate(self.checkings_list):
                if task["collectionName"] == self.collectionName:
                    self.checkings_list[i].collectionName = task["collectionName"]
                    return
            for i, task in enumerate(self.sortings_list):
                if task["collectionName"] == self.collectionName:
                    self.sortings_list[i].collectionName = task["collectionName"]
                    return
            self.collectionName = name
            self._collections.collectionName = name
            self.save_to_file()

    @Slot(str)
    def createCollection(self, name):
        with self._data_lock:
            if name in self._collections.collections:
                name = self._getDefaultSpreadsheetName()
                self._collections.collectionName = name
                self.signal.emit({"type": "input_text_changed", "value": name})
            self._collections.collections[name] = collectionElement([self.rowHeight(-1)], [self.columnWidth(-1)])
            self.beginResetModel()
            self.collectionName = name
            self._collections.collectionName = name
            self._collection = self._collections.collections[name]
            self._data = self._collection.data
            self._roles = self._collection.roles
            self._rowHeights = self._collection.rowHeights
            self._columnWidths = self._collection.columnWidths
            self.collections = self._collections.collections
            self.endResetModel()
            self.save_to_file()

    @Slot(str)
    def deleteCollection(self, name):
        with self._data_lock:
            if name in self.collections:
                del self.collections[name]
                if not self.collections:
                    self.collectionName = self._getDefaultSpreadsheetName()
                    self.createCollection(self.collectionName)
                else:
                    self.beginResetModel()
                    self.collectionName = self.collections.keys()[0]
                    self._collection = self.collections[self.collectionName]
                    self._data = self._collection.data
                    self._roles = self._collection.roles
                    self._rowHeights = self._collection.rowHeights
                    self._columnWidths = self._collection.columnWidths
                    self.endResetModel()
                self.signal.emit({"type": "input_text_changed", "value": self._collections.collectionName})
                self.save_to_file()

    @Slot(str)
    def pressEnterOnInput(self, name):
        """Handle Enter key press on input field."""
        if not self.loadSpreadsheet(name):
            self.collectionName = name
            self.createCollection(name)

    @Slot(str, result=bool)
    def loadSpreadsheet(self, name):
        """Load a spreadsheet by name."""
        collection = self._collections.collections.get(name, {})
        if collection:
            self.beginResetModel()
            self.collectionName = name
            self._collection = collection
            self._data = collection.data
            self._roles = collection.roles
            self._rowHeights = collection.rowHeights
            self._columnWidths = collection.columnWidths
            self.endResetModel()
            with self._data_lock:
                for i, task in enumerate(self._collections.checkings_list[1:], start=1):
                    if task["collectionName"] == name:
                        self._collections.checkings_list.insert(1, task)
                        del self._collections.checkings_list[i+1]
                        break
                for i, task in enumerate(self._collections.sortings_list[1:], start=1):
                    if task["collectionName"] == name:
                        self._collections.sortings_list.insert(1, task)
                        del self._collections.sortings_list[i+1]
                        break
            return True
        else:
            self.signal.emit({"type": "input_text_changed", "value": self.collectionName})
            return False

    @Slot(result=int)
    def rowCount(self, parent=QModelIndex()):
        return self._rows_nb

    @Slot(result=int)
    def columnCount(self, parent=QModelIndex()):
        return self._columns_nb
    
    @Slot(int, result=str)
    def get_cell_color(self, column):
        if column >= len(self._roles):
            return "white"
        elif self._roles[column] == RoleTypes.NAMES:
            return "lightblue"
        elif self._roles[column] == RoleTypes.DEPENDENCIES:
            return "lightgreen"
        elif self._roles[column] == RoleTypes.ATTRIBUTES:
            return "lightyellow"
        elif self._roles[column] == RoleTypes.PATH:
            return "lightcoral"

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            if row < len(self._data) and column < (len(self._data[0]) if self._data else 0):
                return self._data[row][column]
            else:
                return ""
        elif role == Qt.BackgroundRole:
            return self.get_cell_color(column)
        elif role == Qt.DecorationRole:
            if self._selected_row == row and self._selected_column == column:
                return 2
            return int(self._selected_row == row or self._selected_column == column)
        return None

    def _appendChecking(self):
        with self.condition:
            for i, task in enumerate(self.checkings_list[1:], start=1):
                if task["collectionName"] == self.collectionName:
                    del self.checkings_list[i]
                    return
            task_object = {"collectionName": self.collectionName, "id": random.random()}
            self.checkings_list.insert(bool(self.checkings_list), task_object)
            self.condition.notify_all()
            self.save_to_file()

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            row, col = index.row(), index.column()
            with self._data_lock:
                prev_role = self._roles[col] if col < len(self._roles) else RoleTypes.NAMES
                if row >= len(self._data):
                    for r in range(len(self._data), row + 1):
                        prevHeight = self._rowHeights[-1] if self._data else 0
                        self._rowHeights.append(prevHeight + self.rowHeight(-1))
                        self._data.append([""] * (len(self._data[0]) if self._data else 0))
                elif row == len(self._data) - 1 and value == "":
                    self._data[row][col] = ""
                    prev_col_nb = len(self._data[0])
                    for r in range(row, -1, -1):
                        if self._data[r] == [""] * len(self._data[0]):
                            self._data.pop(r)
                            self._rowHeights.pop(r)
                if self._data:
                    if col >= len(self._data[0]):
                        prev_col_nb = len(self._data[0])
                        for r in self._data:
                            for _ in range(prev_col_nb, col + 1):
                                r.append("")
                        for j in range(prev_col_nb, col + 1):
                            prevWidth = self._columnWidths[-1] if len(self._columnWidths) else 0
                            self._columnWidths.append(prevWidth + self.columnWidth(-1))
                            self._roles.append(RoleTypes.ATTRIBUTES)
                        index = self.index(0, prev_col_nb)
                        index2 = self.index(self._rows_nb - 1, col)
                        self.dataChanged.emit(index, index2, [Qt.BackgroundRole])
                        self.signal.emit({"type": "selected_cell_changed", "value": self._role_types.index(RoleTypes.ATTRIBUTES)})
                    elif col == len(self._data[0]) - 1 and value == "":
                        removed_col = False
                        for c in range(col, -1, -1):
                            if all(_row[c] == "" for _row in self._data):
                                removed_col = True
                                for r in self._data:
                                    r.pop(c)
                                self._columnWidths.pop(c)
                                self._roles.pop(c)
                        if removed_col:
                            index = self.index(0, len(self._data[0]))
                            index2 = self.index(self._rows_nb - 1, col)
                            self.dataChanged.emit(index, index2, [Qt.BackgroundRole])
                            if prev_role != RoleTypes.NAMES:
                                self.signal.emit({"type": "selected_cell_changed", "value": self._role_types.index(RoleTypes.NAMES)})
                elif self._roles:
                    self._columnWidths = []
                    index = self.index(0, 0)
                    index2 = self.index(self._rows_nb - 1, prev_col_nb)
                    self.dataChanged.emit(index, index2, [Qt.BackgroundRole])
                    self._roles = []
                    if prev_role != RoleTypes.NAMES:
                        self.signal.emit({"type": "selected_cell_changed", "value": self._role_types.index(RoleTypes.NAMES)})
                if row < len(self._data) and col < len(self._data[0]):
                    self._data[row][col] = value
                self.verticalScroll(self._verticalScrollPosition, self._verticalScrollSize, self._tableViewContentY, self._tableViewHeight)
                self.horizontalScroll(self._horizontalScrollPosition, self._horizontalScrollSize, self._tableViewContentX, self._tableViewWidth)
                index = self.index(row, col)
                self.dataChanged.emit(index, index, [Qt.EditRole, Qt.DisplayRole])
            self._appendChecking()
            return True
        return False

    @Slot(int)
    def addRows(self, count):
        self.setRows(self._rows_nb + count)

    @Slot(int)
    def addColumns(self, count):
        self.setColumns(self._columns_nb + count)

    @Slot(int)
    def setRows(self, count):
        if count < 0:
            return
        if count < self._rows_nb:
            self.beginRemoveRows(QModelIndex(), count, self._rows_nb - 1)
            self._rows_nb = count
            self.endRemoveRows()
        elif count > self._rows_nb:
            prev_row_nb = self._rows_nb
            self.beginInsertRows(QModelIndex(), self._rows_nb, count - 1)
            self._rows_nb = count
            self.endInsertRows()
            index = self.index(prev_row_nb, 0)
            index2 = self.index(count - 1, self._columns_nb - 1)
            self.dataChanged.emit(index, index2, [Qt.BackgroundRole, Qt.DecorationRole])

    @Slot(int)
    def setColumns(self, count):
        if count < 0:
            return
        if count < self._columns_nb:
            self.beginRemoveColumns(QModelIndex(), count, self._columns_nb - 1)
            self._columns_nb = count
            self.endRemoveColumns()
            index = self.index(0, 0)
            index2 = self.index(self._rows_nb - 1, self._columns_nb - 1)
            self.dataChanged.emit(index, index2, [Qt.DisplayRole])
        elif count > self._columns_nb:
            prev_col_nb = self._columns_nb
            self.beginInsertColumns(QModelIndex(), self._columns_nb, count - 1)
            self._columns_nb = count
            self.endInsertColumns()
            index = self.index(0, prev_col_nb)
            index2 = self.index(self._rows_nb - 1, count - 1)
            self.dataChanged.emit(index, index2, [Qt.DecorationRole])
    
    @Slot(float, float, float, float, bool)
    def verticalScroll(self, position, size, tableViewContentY, tableViewHeight, start=False):
        self._verticalScrollPosition = position
        self._verticalScrollSize = size
        self._tableViewContentY = tableViewContentY
        self._tableViewHeight = tableViewHeight
        if position >= 1.0 - size and not start:
            self.addRows(1)
        else:
            sizeToReach = tableViewContentY + tableViewHeight
            if self._data and sizeToReach < self._rowHeights[-1]:
                requiredRows = len(self._data)
            else:
                prevHeight = self._rowHeights[-1] if self._data else 0
                requiredRows = len(self._data) + (sizeToReach - prevHeight) // self.rowHeight(-1) + 2
            if requiredRows != self._rows_nb:
                self.setRows(requiredRows)
    
    @Slot(float, float, float, float, bool)
    def horizontalScroll(self, position, size, tableViewContentX, tableViewWidth, start=False):
        self._horizontalScrollPosition = position
        self._horizontalScrollSize = size
        self._tableViewContentX = tableViewContentX
        self._tableViewWidth = tableViewWidth
        if position >= 1.0 - size and not start:
            self.addColumns(1)
        else:
            sizeToReach = tableViewContentX + tableViewWidth
            if self._data and sizeToReach < self._columnWidths[-1]:
                requiredColumns = len(self._data[0])
            else:
                prevWidth = self._columnWidths[-1] if self._data else 0
                requiredColumns = (len(self._data[0]) if self._data else 0) + (sizeToReach - prevWidth) // self.columnWidth(-1) + 1
            if requiredColumns != self._columns_nb:
                self.setColumns(requiredColumns)

    @Slot(result=int)
    def getMaxRow(self):
        return len(self._data)

    @Slot(result=int)
    def getMaxColumn(self):
        return (len(self._data[0]) if self._data else 0)

    def roleNames(self):
        roles = super().roleNames()
        roles[Qt.DecorationRole] = b"decoration"
        roles[Qt.BackgroundRole] = b"background"
        roles[Qt.EditRole] = b"edit"
        roles[Qt.DisplayRole] = b"display"
        return roles

    @Slot(str, result=list)
    def getOtherCollectionNames(self, input_text):
        """Return a list of other collection names."""
        return [
            name
            for name in self.collections.keys()
            if name != input_text
        ]

    def save_to_file(self):
        """Save model data to a JSON file."""
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(self._collections, f)
    
    @Slot(bool)
    def sortButton(self, reorder):
        with self.condition:
            for i, task in enumerate(self._collections.sortings_list):
                if task["collectionName"] == self.collectionName:
                    del self._collections.sortings_list[i]
                    return
            task_object = {"collectionName": self.collectionName, "id": random.random(), "reorder": reorder}
            self._collections.sortings_list.insert(bool(self._collections.sortings_list), task_object)
            self.condition.notify_all()
            with self._data_lock:
                self.save_to_file()
    
    @Slot(int)
    def setColumnRole(self, ind):
        """Set the role for a specific column."""
        if self._selected_column < len(self._roles):
            self._roles[self._selected_column] = self._role_types[ind]
            # Notify views that header row (row 0) needs to update
            index = self.index(0, self._selected_column)
            index2 = self.index(self._rows_nb - 1, self._selected_column)
            self.dataChanged.emit(index, index2, [Qt.BackgroundRole])
            self._appendChecking()
    
    @Slot()
    def showButton(self):
        with self._data_lock:
            url_col = self._roles.index(RoleTypes.PATH) if RoleTypes.PATH in self._roles else -1
            if url_col != -1:
                if not os.path.exists(MEDIA_ROOT):
                    os.makedirs(MEDIA_ROOT)
                show_images(self, [
                    os.path.join(MEDIA_ROOT, self._data[i][url_col])
                    for i in range(len(self._data))
                    if self._data[i][url_col] and os.path.exists(os.path.join(MEDIA_ROOT, self._data[i][url_col]))
                ])
    
    # def _updateCells(self, index1, index2, roles):
    #     if index1.row() == 0:

    
    @Slot(int, int)
    def cellClicked(self, row, column):
        previously_selected_row = self._selected_row
        previously_selected_column = self._selected_column
        self._selected_row = row
        self._selected_column = column
        if row != previously_selected_row:
            if previously_selected_row != -1:
                self.dataChanged.emit(self.index(previously_selected_row, 0), self.index(previously_selected_row, self._columns_nb - 1), [Qt.DecorationRole])
            self.dataChanged.emit(self.index(row, 0), self.index(row, self._columns_nb - 1), [Qt.DecorationRole])
        if column != previously_selected_column:
            if previously_selected_column != -1:
                self.dataChanged.emit(self.index(0, previously_selected_column), self.index(self._rows_nb - 1, previously_selected_column), [Qt.DecorationRole])
            self.dataChanged.emit(self.index(0, column), self.index(self._rows_nb - 1, column), [Qt.DecorationRole])
            
            if column < len(self._roles):
                role_combo = self._role_types.index(self._roles[column])
            else:
                role_combo = self._role_types.index(RoleTypes.NAMES)
            self.signal.emit({"type": "selected_cell_changed", "value": role_combo})