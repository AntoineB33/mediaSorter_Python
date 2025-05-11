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
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
# from .generate_sortings import find_valid_sortings


class SpreadsheetModel(QAbstractTableModel):
    input_text_changed = Signal()# Add these properties and methods to SpreadsheetModel
    column_width_changed = Signal(int)
    row_height_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.default_width = 100
        self.default_height = 30

        self._data = []
        self._rowHeights = []
        self._columnWidths = []
        self._rows_nb = 0
        self._columns_nb = 0
        self._collections = {
            "collections": {},
        }
        self._collectionName = self.getDefaultSpreadsheetName()
        self._maxRow = 0
        self._maxColumn = 0
        self._collection = {"data": self._data, "rowHeights": self._rowHeights,
                            "columnWidths": self._columnWidths, "maxRow": 0, "maxColumn": 0}
        self._collections = {
            "collections": {self._collectionName: self._collection},
            "collectionName": self._collectionName,
        }
        if not Path("data").exists():
            Path("data").mkdir(parents=True, exist_ok=True)
        try:
            with open(f"data/general.json", "r") as f:
                collections = json.load(f)
            if collections:
                self._collections = collections
                self._collectionName = collections["collectionName"]
                self._collection = collections["collections"].get(
                    self._collectionName, {}
                )
                self._data = self._collection["data"]
                self._rowHeights = self._collection["rowHeights"]
                self._columnWidths = self._collection["columnWidths"]
                self._maxRow = self._collection["maxRow"]
                self._maxColumn = self._collection["maxColumn"]
        except FileNotFoundError:
            # No saved data, initialize with defaults if needed
            pass
        except Exception as e:
            print(f"Error loading spreadsheet: {str(e)}")
        self._verticalScrollPosition = 0
        self._verticalScrollSize = 0
        self._tableViewContentY = 0
        self._tableViewHeight = 0
        self._horizontalScrollPosition = 0
        self._horizontalScrollSize = 0
        self._tableViewContentX = 0
        self._tableViewWidth = 0
        self.input_text_changed.emit()

    @Slot(int, result=int)
    def columnWidth(self, column):
        if 0 <= column < len(self._columnWidths):
            return self._columnWidths[column]
        return self.default_width

    @Slot(int, float)
    def updateColumnWidth(self, column, new_width):
        self._columnWidths[column] = new_width
        self.column_width_changed.emit(column)

    @Slot(int, result=int)
    def rowHeight(self, row):
        if 0 <= row < len(self._rowHeights):
            return self._rowHeights[row]
        return self.default_height

    @Slot(int, float)
    def updateRowHeight(self, row, new_height):
        self._rowHeights[row] = new_height
        self.row_height_changed.emit(row)
    
    @Property(str, notify=input_text_changed)
    def input_text(self):
        """Property for the input text."""
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

    @Slot(str)
    def setSpreadsheetName(self, name):
        """Set the current spreadsheet name."""
        if name in self._collections["collections"]:
            return
        self.beginResetModel()
        self._collections["collections"][name] = self._collection
        del self._collections["collections"][self._collectionName]
        self._collectionName = name
        self.endResetModel()
        self.save_to_file()

    @Slot(str)
    def createCollection(self, name):
        """Create a new collection with the given name."""
        if name in self._collections["collections"]:
            name = self.getDefaultSpreadsheetName()
            self._collectionName = name
            self.input_text_changed.emit()
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
        self._maxRow = 0
        self._maxColumn = 0
        self.endResetModel()
        self.save_to_file()

    @Slot(str)
    def deleteCollection(self, name):
        """Remove a collection by name."""
        if name in self._collections["collections"]:
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
            self._maxRow = self._collection["maxRow"]
            self._maxColumn = self._collection["maxColumn"]
            self.endResetModel()
            self.input_text_changed.emit()
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
            self._maxRow = self._collection["maxRow"]
            self._maxColumn = self._collection["maxColumn"]
            self.endResetModel()
            self.save_to_file()
            return True
        else:
            self.input_text_changed.emit()
            return False

    def rowCount(self, parent=None):
        return self._rows_nb

    def columnCount(self, parent=None):
        return self._columns_nb

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.isValid():
            if index.row() < self._maxRow and index.column() < self._maxColumn:
                return self._data[index.row()][index.column()]
            else:
                return ""
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            row = index.row()
            col = index.column()
            if row >= self._maxRow:
                for r in range(self._maxRow, row + 1):
                    self._data.append([""] * self._maxColumn)
                    self._rowHeights.append(self.default_height)
                self._maxRow = row + 1
                self._collection["maxRow"] = self._maxRow
            elif row == self._maxRow - 1 and value == "":
                for r in range(row - 1, 0, -1):
                    if self._data[r] == [""] * self._maxColumn:
                        self._maxRow = r - 1
                        self._collection["maxRow"] = self._maxRow
                        self._data.pop(r)
                        self._rowHeights.pop(r)
                        break
            if col >= self._maxColumn:
                for r in self._data:
                    for _ in range(self._maxColumn, col + 1):
                        r.append("")
                    self._columnWidths.append(self.default_width)
                self._maxColumn = col + 1
                self._collection["maxColumn"] = self._maxColumn
            elif col == self._maxColumn - 1 and value == "":
                for c in range(col - 1, 0, -1):
                    if all(row[c] == "" for row in self._data):
                        self._maxColumn = c
                        self._collection["maxColumn"] = self._maxColumn
                        for r in self._data:
                            r.pop(c)
                        self._columnWidths.pop(c)
                        break
            if row < self._maxRow and col < self._maxColumn:
                self._data[row][col] = value
            # TODO
            # self.verticalScroll(self._verticalScrollPosition, self._verticalScrollSize, self._tableViewContentY, self._tableViewHeight)
            # self.horizontalScroll(self._horizontalScrollPosition, self._horizontalScrollSize, self._tableViewContentX, self._tableViewWidth)
            self.dataChanged.emit(index, index, [Qt.EditRole, Qt.DisplayRole])
            self.save_to_file()
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
        if start:
            return
        if position >= 1.0 - size:
            self.addRows(1)
        else:
            n = int((tableViewContentY + tableViewHeight) / self.default_height + 1)
            requiredRows = max(self._maxRow + 1, n)
            currentRows = self.rowCount()
            if requiredRows != currentRows:
                self.setRows(requiredRows)
    
    @Slot(float, float, float, float, bool)
    def horizontalScroll(self, position, size, tableViewContentX, tableViewWidth, start=False):
        self._horizontalScrollPosition = position
        self._horizontalScrollSize = size
        self._tableViewContentX = tableViewContentX
        self._tableViewWidth = tableViewWidth
        if start:
            return
        if position >= 1.0 - size:
            self.addColumns(1)
        else:
            n = int((tableViewContentX + tableViewWidth) / self.default_width + 1)
            requiredCols = max(self._maxColumn + 1, n)
            currentCols = self.columnCount()
            if requiredCols != currentCols:
                self.setColumns(requiredCols)

    @Slot(result=int)
    def getMaxRow(self):
        return self._maxRow

    @Slot(result=int)
    def getMaxColumn(self):
        return self._maxColumn

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
                "maxRow": self._maxRow,
                "maxColumn": self._maxColumn,
            }
            self._collectionName = name
            self.save_to_file()
        else:
            print(f"Collection '{name}' already exists.")

    def save_to_file(self):
        """Save model data to a JSON file."""
        with open(f"data/general.json", "w") as f:
            json.dump(self._collections, f)
