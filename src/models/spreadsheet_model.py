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


SAVE_FILE = "data/general.json"

class TaskTypes:
    CHECKINGS = "checkings"
    SORTINGS = "sortings"
    STOP_SORTING = "stop_sorting"
    CHANGE_COLLECTION = "change_collection"
    SET_DATA = "setData"
    SET_COLLECTION_NAME = "setCollectionName"
    CREATE_COLLECTION = "createCollection"
    DELETE_COLLECTION = "deleteCollection"

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

class AsyncTask:
    def __init__(self, task_type, collectionName = None, row = None, column = None, value = None, onlyCalculate=False):
        self.task_type = task_type
        self.collectionName = collectionName
        self.row = row
        self.column = column
        self.value = value
        self.onlyCalculate = onlyCalculate
        self.id = random.random()

class SpreadsheetModel(QAbstractTableModel):
    signal = Signal(dict)
    ortools_loaded = threading.Event()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.default_width = 100
        self.horizontal_padding = 5
        self.vertical_padding = 5
        self.font = QFont("Arial", 10)

        self.metrics = QFontMetrics(self.font)
        self.condition = threading.Condition()
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
        self._data_lock = asyncio.Lock()
        self._executor = ThreadPoolExecutor(max_workers=2)
            
    async def initialize(self):
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
            self._collections.collectionName = self._getDefaultSpreadsheetName()
            await self.createCollection(self._collections.collectionName)
        self._executor.submit(self.run_async, self.checkings_thread)
        self._executor.submit(self.run_async, self.sortings_thread)

    def run_async(self, coro_func):
        """Helper to run coroutines in a new event loop per thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro_func())

    async def add_task(self, task_object):
        with self.condition:
            task_type = task_object.task_type
            collectionName = task_object.collectionName
            match task_type:
                case TaskTypes.CHECKINGS:
                    for i, task in enumerate(self._collections.checkings_list[1:], start=1):
                        if task.collectionName == collectionName:
                            del self._collections.checkings_list[i]
                            return
                    self._collections.checkings_list.insert(bool(self._collections.checkings_list), task_object)
                    self.save_to_file()
                case TaskTypes.SORTINGS:
                    for i, task in enumerate(self._collections.sortings_list[1:], start=1):
                        if task.collectionName == collectionName:
                            del self._collections.sortings_list[i]
                            return
                    self._collections.sortings_list.insert(bool(self._collections.sortings_list), task_object)
                case TaskTypes.STOP_SORTING:
                    if self._collections.sortings_list[0].collectionName == collectionName:
                        self._collections.sortings_list.insert(1, task_object)
                    else:
                        for i, task in enumerate(self._collections.sortings_list[1:], start=1):
                            if task.collectionName == collectionName:
                                del self._collections.sortings_list[i]
                                return
                case TaskTypes.CHANGE_COLLECTION:
                    for i, task in enumerate(self._collections.checkings_list[1:], start=1):
                        if task.collectionName == collectionName:
                            self._collections.checkings_list.insert(1, task)
                            del self._collections.checkings_list[i+1]
                            break
                    for i, task in enumerate(self._collections.sortings_list[1:], start=1):
                        if task.collectionName == collectionName:
                            self._collections.sortings_list.insert(1, task)
                            del self._collections.sortings_list[i+1]
                            break
                case TaskTypes.SET_DATA:
                    row, col, value = task_object.row, task_object.column, task_object.value
                    async with self._data_lock:
                        if row >= len(self._data):
                            for r in range(len(self._data), row + 1):
                                prevHeight = self._rowHeights[-1] if self._data else 0
                                self._rowHeights.append(prevHeight + self.rowHeight(-1))
                                self._data.append([""] * (len(self._data[0]) if self._data else 0))
                        elif row == len(self._data) - 1 and value == "":
                            self._data[row][col] = ""
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
                                    self._roles.append("categories")
                                index = self.index(0, prev_col_nb)
                                index2 = self.index(0, col)
                                self.dataChanged.emit(index, index2, [Qt.BackgroundRole])
                            elif col == len(self._data[0]) - 1 and value == "":
                                for c in range(col, -1, -1):
                                    if all(_row[c] == "" for _row in self._data):
                                        for r in self._data:
                                            r.pop(c)
                                        self._columnWidths.pop(c)
                                        self._roles.pop(c)
                                index = self.index(0, len(self._data[0]))
                                index2 = self.index(0, col)
                                self.dataChanged.emit(index, index2, [Qt.BackgroundRole])
                        elif self._roles:
                            self._columnWidths = []
                            index = self.index(0, 0)
                            index2 = self.index(0, len(self._roles))
                            self.dataChanged.emit(index, index2, [Qt.BackgroundRole])
                            self._roles = []
                        if row < len(self._data) and col < len(self._data[0]):
                            self._data[row][col] = value
                        self.verticalScroll(self._verticalScrollPosition, self._verticalScrollSize, self._tableViewContentY, self._tableViewHeight)
                        self.horizontalScroll(self._horizontalScrollPosition, self._horizontalScrollSize, self._tableViewContentX, self._tableViewWidth)
                        index = self.index(row, col)
                        self.dataChanged.emit(index, index, [Qt.EditRole, Qt.DisplayRole])
                        if self._collections.checkings_list and self._collections.checkings_list[0].collectionName == collectionName:
                            self._collections.checkings_list[0].id = random.random()
                        else:
                            for i, task in enumerate(self._collections.checkings_list):
                                if task.collectionName == collectionName:
                                    del self._collections.checkings_list[i]
                                    return
                            self._collections.checkings_list.insert(bool(self._collections.checkings_list), task_object)
                        self.save_to_file()
                        asyncio.create_task(self.add_task(AsyncTask(TaskTypes.CHECKINGS, collectionName)))
                case TaskTypes.SET_COLLECTION_NAME:
                    async with self._data_lock:
                        if collectionName in self._collections.collections:
                            return
                        self._collections.collections[collectionName] = self._collection
                        del self._collections.collections[self._collections.collectionName]
                        for i, task in enumerate(self._collections.checkings_list):
                            if task.collectionName == self._collections.collectionName:
                                self._collections.checkings_list[i].collectionName = task.collectionName
                                return
                        for i, task in enumerate(self._collections.sortings_list):
                            if task.collectionName == self._collections.collectionName:
                                self._collections.sortings_list[i].collectionName = task.collectionName
                                return
                        self._collections.collectionName = collectionName
                        self.save_to_file()
                case TaskTypes.CREATE_COLLECTION:
                    async with self._data_lock:
                        if collectionName in self._collections.collections:
                            collectionName = self._getDefaultSpreadsheetName()
                            self._collections.collectionName = collectionName
                            self.signal.emit({"type": "input_text_changed", "value": self._collections.collectionName})
                        self._collections.collections[collectionName] = collectionElement([self.rowHeight(-1)], [self.columnWidth(-1)])
                        self.beginResetModel()
                        self._collections.collectionName = collectionName
                        self._collection = self._collections.collections[collectionName]
                        self._data = self._collection.data
                        self._roles = self._collection.roles
                        self._rowHeights = self._collection.rowHeights
                        self._columnWidths = self._collection.columnWidths
                        self.endResetModel()
                        self.save_to_file()
                case TaskTypes.DELETE_COLLECTION:
                    async with self._data_lock:
                        if collectionName in self._collections.collections:
                            del self._collections.collections[collectionName]
                            if not self._collections.collections:
                                await self.createCollection(self._getDefaultSpreadsheetName())
                            else:
                                self.beginResetModel()
                                self._collections.collectionName = self._collections.collections.keys()[0]
                                self._collection = self._collections.collections[self._collections.collectionName]
                                self._data = self._collection.data
                                self._roles = self._collection.roles
                                self._rowHeights = self._collection.rowHeights
                                self._columnWidths = self._collection.columnWidths
                                self.endResetModel()
                            self.signal.emit({"type": "input_text_changed", "value": self._collections.collectionName})
                            self.save_to_file()
            self.condition.notify_all()
     
    async def checkings_thread(self):
        global find_valid_sortings
        from models.generate_sortings import find_valid_sortings
        self.ortools_loaded.set()
        firstIteration = True
        while True:
            task = None
            with self.condition:
                if not firstIteration:
                    del self._collections.checkings_list[0]
                firstIteration = False
                while not self._collections.checkings_list:
                    self.condition.wait()
                task = self._collections.checkings_list[0]
            data = self._collections.collections[task.collectionName].data
            roles = self._collections.collections[task.collectionName].roles
            res = find_valid_sortings(data, roles)
            if type(res) is str:
                self._errorMsg = res
                self.signal.emit({"type": "FloatingWindow_text_changed", "value": res})
            else:
                if self._errorMsg:
                    self._errorMsg = ""
                    self.signal.emit({"type": "FloatingWindow_text_changed", "value": ""})
    
    async def sortings_thread(self):
        self.ortools_loaded.wait()
        firstIteration = True
        while True:
            with self.condition:
                if not firstIteration:
                    del self._collections.checkings_list[0]
                firstIteration = False
                while not self._collections.checkings_list:
                    self.condition.wait()
                task = self._collections.sortings_list[0]
                collectionName = task.collectionName
                task_id = task.id
            data = self._collections.collections[collectionName].data
            roles = self._collections.collections[collectionName].roles
            res = find_valid_sortings(data, roles)
            async with self._data_lock:
                if self._collections.sortings_list[0][1] != task_id:
                    continue
                if type(res) is str:
                    for e in self._errorMsg:
                        if e[0] == collectionName:
                            e[1] = res
                            break
                    else:
                        self._errorMsg.append([collectionName, res])
                    self.signal.emit({"type": "FloatingWindow_text_changed", "value": "\n".join([" : ".join(e) for e in self._errorMsg])})
                else:
                    try:
                        self._errorMsg.remove(e)
                        self.signal.emit({"type": "FloatingWindow_text_changed", "value": "\n".join([" : ".join(e) for e in self._errorMsg])})
                    except ValueError:
                        pass
                    if res[0] != list(range(len(data))):
                        if collectionName == self._collections.collectionName:
                            self.beginResetModel()
                            self._data = [data[i] for i in res[0]]
                            for r in self._data:
                                for c in r:
                                    match = re.match(r'after\s+([1-9][0-9]*)', c)
                                    if match:
                                        j = int(match.group(1)) - 1
                                        c = re.sub(r'(after\s+)([1-9][0-9]*)', r'\1' + data.index(j), c)
                                    else:
                                        match = re.match(r'as far as possible from (\d+)', c)
                                        if match:
                                            X = int(match.group(1)) - 1
                                            c = re.sub(r'as far as possible from (\d+)', f'as far as possible from {data.index(X)}', c)
                            for i in range(len(self._data) - 1, -1, -1):
                                if self._data[i] == [""] * len(self._data[0]):
                                    self._data.pop(i)
                                    self._rowHeights.pop(i)
                            self.verticalScroll(self._verticalScrollPosition, self._verticalScrollSize, self._tableViewContentY, self._tableViewHeight)
                            self.endResetModel()
                            self.save_to_file()

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
    
    @Slot(int, int, result=str)
    def get_cell_color(self, row, column):
        if row != 0 or column >= len(self._roles):
            return "white"
        elif self._roles[column] == "names":
            return "lightblue"
        elif self._roles[column] == "dependencies":
            return "lightgreen"
        elif self._roles[column] == "categories":
            return "lightyellow"
    
    @Slot(result=str)
    def get_collectionName(self):
        return self._collections.collectionName

    @Slot(result=str)
    def getCollectionName(self):
        """Return the current collection name."""
        return self._collections.collectionName

    def _getDefaultSpreadsheetName(self):
        """Generate a default spreadsheet name not already used."""
        i = 1
        while f"Default_{i}" in self._collections.collections:
            i += 1
        return f"Default_{i}"

    @asyncSlot(str)
    async def setSpreadsheetName(self, name):
        asyncio.create_task(self.add_task(AsyncTask(TaskTypes.SET_COLLECTION_NAME, collectionName=name)))

    @asyncSlot(str)
    async def createCollection(self, name):
        asyncio.create_task(self.add_task(AsyncTask(TaskTypes.CREATE_COLLECTION, collectionName=name)))

    @asyncSlot(str)
    async def deleteCollection(self, name):
        asyncio.create_task(self.add_task(AsyncTask(TaskTypes.DELETE_COLLECTION, collectionName=name)))

    @Slot(str)
    async def pressEnterOnInput(self, name):
        """Handle Enter key press on input field."""
        if not self.loadSpreadsheet(name):
            self.createCollection(name)

    @Slot(str, result=bool)
    def loadSpreadsheet(self, name):
        """Load a spreadsheet by name."""
        collection = self._collections.collections.get(name, {})
        if collection:
            self.beginResetModel()
            self._collections.collectionName = name
            self._collection = collection
            self._data = self._collection.data
            self._roles = self._collection.roles
            self._rowHeights = self._collection.rowHeights
            self._columnWidths = self._collection.columnWidths
            self.endResetModel()
            return True
        else:
            self.signal.emit({"type": "input_text_changed", "value": self._collections.collectionName})
            return False

    @Slot(result=int)
    def rowCount(self, parent=QModelIndex()):
        return self._rows_nb

    @Slot(result=int)
    def columnCount(self, parent=QModelIndex()):
        return self._columns_nb

    def data(self, index, role=Qt.DisplayRole):
        print(f"Requested role: {role}")
        if role == Qt.DisplayRole and index.isValid():
            if index.row() < len(self._data) and index.column() < (len(self._data[0]) if self._data else 0):
                return self._data[index.row()][index.column()]
            else:
                return ""
        elif role == Qt.BackgroundRole:
            return self.get_cell_color(index.row(), index.column())
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            asyncio.create_task(self.add_task(AsyncTask(TaskTypes.SET_DATA, row = index.row(), column = index.column(), value=value)))
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
            self.beginInsertRows(QModelIndex(), self._rows_nb, count - 1)
            self._rows_nb = count
            self.endInsertRows()

    @Slot(int)
    def setColumns(self, count):
        if count < 0:
            return
        if count < self._columns_nb:
            self.beginRemoveColumns(QModelIndex(), count, self._columns_nb - 1)
            self._columns_nb = count
            self.endRemoveColumns()
        elif count > self._columns_nb:
            self.beginInsertColumns(QModelIndex(), self._columns_nb, count - 1)
            self._columns_nb = count
            self.endInsertColumns()
    
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
        return {Qt.DisplayRole: b"display"}

    @Slot(str, result=list)
    def getOtherCollectionNames(self, input_text):
        """Return a list of other collection names."""
        return [
            name
            for name in self._collections.collections.keys()
            if name != input_text
        ]

    @Slot(str)
    def setCollectionName(self, name):
        """Set the current collection name."""
        if name not in self._collections.collections:
            self._collections.collections[name] = {
                "data": self._data,
                "roles": self._roles,
                "rowHeights": self._rowHeights,
                "columnWidths": self._columnWidths,
            }
            self._collections.collectionName = name
            self.save_to_file()
        else:
            print(f"Collection '{name}' already exists.")

    def save_to_file(self):
        """Save model data to a JSON file."""
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(self._collections, f)
    
    @Slot(bool)
    def sortButton(self, onlyCalculate):
        asyncio.create_task(self.add_task(AsyncTask(TaskTypes.SORTINGS, self._collections.collectionName, onlyCalculate=onlyCalculate)))
    
    @Slot(int, str)
    def setColumnRole(self, column, role):
        """Set the role for a specific column."""
        if column < len(self._roles):
            self._roles[column] = role
            # Notify views that header row (row 0) needs to update
            index = self.index(0, column)
            self.dataChanged.emit(index, index, [Qt.DisplayRole])
        asyncio.create_task(self.add_task(AsyncTask(TaskTypes.CHECKINGS, self._collections.collectionName)))