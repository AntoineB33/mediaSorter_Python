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

class SpreadsheetModel(QAbstractTableModel):
    signal = Signal(dict)
    ortools_loaded = threading.Event()

    def __init__(self, parent=None):
        super().__init__()

        self.default_width = 100
        self.horizontal_padding = 5
        self.vertical_padding = 5
        self.font = QFont("Arial", 10)

        self.metrics = QFontMetrics(self.font)
        self.checkings_condition = asyncio.Condition()
        if not Path("data").exists():
            Path("data").mkdir(parents=True, exist_ok=True)
        try:
            with open(f"data/general.json", "r") as f:
                collections = json.load(f)
            if collections:
                self._collections = collections
                self._collectionName = collections["collectionName"]
                self.loadSpreadsheet(self._collectionName)
                self.checkings_deque = collections["checkings_deque"]
                self.sortings_deque = collections["sortings_deque"]
        except FileNotFoundError:
            self.checkings_deque = []
            self.sortings_deque = []
            self._data = []
            self._rowHeights = []
            self._columnWidths = []
            self._rows_nb = 0
            self._columns_nb = 0
            self._collections = {
                "collections": {},
            }
            self._collectionName = self.getDefaultSpreadsheetName()
            self._collection = {"data": self._data, "rowHeights": self._rowHeights,
                                "columnWidths": self._columnWidths}
            self._collections = {
                "collections": {self._collectionName: self._collection},
                "collectionName": self._collectionName,
                "checkings_deque": self.checkings_deque,
                "sortings_deque": self.sortings_deque,
            }
        self._verticalScrollPosition = 0
        self._verticalScrollSize = 0
        self._tableViewContentY = 0
        self._tableViewHeight = 0
        self._horizontalScrollPosition = 0
        self._horizontalScrollSize = 0
        self._tableViewContentX = 0
        self._tableViewWidth = 0
        self._data_lock = asyncio.Lock()
            
    def _start_async_tasks(self):
        print("Starting async tasks")
        asyncio.create_task(self.checkings_worker())

        asyncio.create_task(self.add_task(["load_ortools", None]))
        for collection_name in self.checkings_deque:
            asyncio.create_task(self.add_task(["checkings", collection_name]))
        for collection_name in self.sortings_deque:
            asyncio.create_task(self.add_task(["sortings", collection_name]))

    async def add_task(self, task_name):
        async with self.checkings_condition:
            if task_name[0] == "checkings":
                for i, task in enumerate(self.checkings_deque):
                    if task[0] == task_name[0] and task[1] == task_name[1]:
                        del self.checkings_deque[i]
                        return
                self.checkings_deque.insert(0, task_name)
            elif task_name[0] == "sortings":
                for i, task in enumerate(self.sortings_deque):
                    if task[0] == task_name[0] and task[1] == task_name[1]:
                        del self.sortings_deque[i]
                        return
                self.sortings_deque.insert(0, task_name)
            elif task_name[0] == "change_collection":
                for i, task in enumerate(self.checkings_deque):
                    if task[0] == "checkings" and task[1] == task_name[1]:
                        self.checkings_deque.insert(0, task)
                        del self.checkings_deque[i]
                        break
            else:
                self.checkings_deque.insert(0, task_name)
            self.checkings_condition.notify()
            print(f"Task added: {task_name[0]} for collection {task_name[1]}")
        
    async def checkings_worker(self):
        print("Task worker started")
        while True:
            async with self.checkings_condition:
                # Wait until deque is not empty
                await self.checkings_condition.wait_for(lambda: len(self.checkings_deque) > 0)
                task = self.checkings_deque[0]
            if task[0] == "load_ortools":
                global find_valid_sortings
                from models.generate_sortings import find_valid_sortings
                self.ortools_loaded.set()
            if task[0] == "checkings":
                self.ortools_loaded.wait()
                data = self._collections["collections"][task[1]]["data"]
                res = find_valid_sortings(data)
                if type(res) is str:
                    self.signal.emit({"type": "FloatingWindow_text_changed", "value": res})
                else:
                    async with self._data_lock:
                        if task[1] == self._collectionName:
                            self.beginResetModel()
                            self._data = [data[i] for i in res[0]]
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
    
    @Slot(result=str)
    def get_collectionName(self):
        return self._collectionName

    @Slot(result=str)
    def getCollectionName(self):
        """Return the current collection name."""
        return self._collectionName

    @Slot(result=str)
    def getDefaultSpreadsheetName(self):
        """Generate a default spreadsheet name not already used."""
        i = 1
        while f"Default_{i}" in self._collections["collections"]:
            i += 1
        return f"Default_{i}"

    @asyncSlot(str)
    async def setSpreadsheetName(self, name):
        """Set the current spreadsheet name."""
        if name in self._collections["collections"]:
            return
        async with self._data_lock:
            self.beginResetModel()
            self._collections["collections"][name] = self._collection
            del self._collections["collections"][self._collectionName]
            self._collectionName = name
            self.endResetModel()
            self.save_to_file()

    @asyncSlot(str)
    async def createCollection(self, name):
        """Create a new collection with the given name."""
        if name in self._collections["collections"]:
            name = self.getDefaultSpreadsheetName()
            self._collectionName = name
            self.signal.emit({"type": "input_text_changed", "value": self._collectionName})
        async with self._data_lock:
            self._collections["collections"][name] = {
                "data": [],
                "rowHeights": [],
                "columnWidths": [],
                "maxRow": 0,
                "maxColumn": 0,
            }
            self.beginResetModel()
            self._collectionName = name
            self._collection = self._collections["collections"][name]
            self._data = self._collection["data"]
            self._rowHeights = self._collection["rowHeights"]
            self._columnWidths = self._collection["columnWidths"]
            self.endResetModel()
            self.save_to_file()

    @asyncSlot(str)
    async def deleteCollection(self, name):
        """Remove a collection by name."""
        if name in self._collections["collections"]:
            async with self._data_lock:
                self.beginResetModel()
                del self._collections["collections"][name]
                if not self._collections["collections"]:
                    self._collections["collections"] = {
                        self.getDefaultSpreadsheetName(): {
                            "data": [],
                            "rowHeights": [],
                            "columnWidths": [],
                            "maxRow": 0,
                            "maxColumn": 0,
                        }
                    }
                self._collectionName = self._collections["collections"].keys()[0]
                self._collection = self._collections["collections"][self._collectionName]
                self._data = self._collection["data"]
                self._rowHeights = self._collection["rowHeights"]
                self._columnWidths = self._collection["columnWidths"]
                self.endResetModel()
                self.signal.emit({"type": "input_text_changed", "value": self._collectionName})
                self.save_to_file()

    @Slot(str)
    def pressEnterOnInput(self, name):
        """Handle Enter key press on input field."""
        if not self.loadSpreadsheet(name):
            self.createCollection(name)

    @Slot(str, result=bool)
    def loadSpreadsheet(self, name):
        """Load a spreadsheet by name."""
        collection = self._collections["collections"].get(name, {})
        if collection:
            self.beginResetModel()
            self._collectionName = name
            self._collection = collection
            self._data = self._collection["data"]
            self._rowHeights = self._collection["rowHeights"]
            self._columnWidths = self._collection["columnWidths"]
            self.endResetModel()
            self.save_to_file()
            return True
        else:
            self.signal.emit({"type": "input_text_changed", "value": self._collectionName})
            return False

    @Slot(result=int)
    def rowCount(self, parent=None):
        return self._rows_nb

    @Slot(result=int)
    def columnCount(self, parent=None):
        return self._columns_nb

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.isValid():
            if index.row() < len(self._data) and index.column() < (len(self._data[0]) if self._data else 0):
                return self._data[index.row()][index.column()]
            else:
                return ""
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            row = index.row()
            col = index.column()
            if row >= len(self._data):
                for r in range(len(self._data), row + 1):
                    prevHeight = self._rowHeights[-1] if self._data else 0
                    self._rowHeights.append(prevHeight + self.rowHeight(-1))
                    self._data.append([""] * (len(self._data[0]) if self._data else 0))
            elif row == len(self._data) - 1 and value == "":
                for r in range(row - 1, -1, -1):
                    if self._data[r] == [""] * len(self._data[0]):
                        self._data.pop(r)
                        self._rowHeights.pop(r)
                        break
            if self._data:
                if col >= len(self._data[0]):
                    prev_col_nb = len(self._data[0])
                    for r in self._data:
                        for _ in range(prev_col_nb, col + 1):
                            r.append("")
                    for _ in range(prev_col_nb, col + 1):
                        prevWidth = self._columnWidths[-1] if len(self._columnWidths) else 0
                        self._columnWidths.append(prevWidth + self.columnWidth(-1))
                elif col == len(self._data[0]) - 1 and value == "":
                    for c in range(col - 1, 0, -1):
                        if all(row[c] == "" for row in self._data):
                            for r in self._data:
                                r.pop(c)
                            self._columnWidths.pop(c)
                            break
            if row < len(self._data) and col < len(self._data[0]):
                self._data[row][col] = value
            self.verticalScroll(self._verticalScrollPosition, self._verticalScrollSize, self._tableViewContentY, self._tableViewHeight)
            self.horizontalScroll(self._horizontalScrollPosition, self._horizontalScrollSize, self._tableViewContentX, self._tableViewWidth)
            self.dataChanged.emit(index, index, [Qt.EditRole, Qt.DisplayRole])
            self.save_to_file()
            asyncio.create_task(self.add_task(["checkings", self._collectionName]))
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
            for name in self._collections["collections"].keys()
            if name != input_text
        ]

    @Slot(str)
    def setCollectionName(self, name):
        """Set the current collection name."""
        if name not in self._collections["collections"]:
            self._collections["collections"][name] = {
                "data": self._data,
                "rowHeights": self._rowHeights,
                "columnWidths": self._columnWidths,
            }
            self._collectionName = name
            self.save_to_file()
        else:
            print(f"Collection '{name}' already exists.")

    def save_to_file(self):
        """Save model data to a JSON file."""
        with open(f"data/general.json", "w") as f:
            json.dump(self._collections, f)
    
    @Slot()
    def sortButton(self):
        self._sortings_wip.append(self._collectionName)
        threading.Thread(target=self.thread_function).start()