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
        self._data = []
        self._rows_nb = 0
        self._columns_nb = 0
        self._collections = {
            "collections": {},
        }
        self._collectionName = self.getDefaultSpreadsheetName()
        self._maxRow = 0
        self._maxColumn = 0
        self._collection = {"maxRow": 0, "maxColumn": 0, "data": []}
        self._collections = {
            "collections": {self._collectionName: self._collection},
            "collectionName": self._collectionName,
        }
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
                self._maxRow = self._collection["maxRow"]
                self._maxColumn = self._collection["maxColumn"]
        except FileNotFoundError:
            # No saved data, initialize with defaults if needed
            pass
        except Exception as e:
            print(f"Error loading spreadsheet: {str(e)}")
        self.input_text_changed.emit()

    @Slot(int, result=int)
    def columnWidth(self, column):
        if 0 <= column < len(self._collection["columnWidths"]):
            return self._collection["columnWidths"][column]
        return 100

    @Slot(int, int)
    def updateColumnWidth(self, column, new_width):
        if column >= len(self._collection["columnWidths"]):
            self._collection["columnWidths"].extend([100]*(column - len(self._collection["columnWidths"]) + 1))
        if new_width > self._collection["columnWidths"][column]:
            self._collection["columnWidths"][column] = new_width
            self.column_width_changed.emit(column)

    @Slot(int, result=int)
    def rowHeight(self, row):
        if 0 <= row < len(self._collection["rowHeights"]):
            return self._collection["rowHeights"][row]
        return 30

    @Slot(int, int)
    def updateRowHeight(self, row, new_height):
        if row >= len(self._collection["rowHeights"]):
            self._collection["rowHeights"].extend([30]*(row - len(self._collection["rowHeights"]) + 1))
        if new_height > self._collection["rowHeights"][row]:
            self._collection["rowHeights"][row] = new_height
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
            "maxRow": 0,
            "maxColumn": 0,
        }
        self.beginResetModel()
        self._collectionName = name
        self._collection = self._collections["collections"][name]
        self._data = self._collection["data"]
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
                        "maxRow": 0,
                        "maxColumn": 0,
                        "data": [],
                    }
                }
            self._collectionName = self._collections["collections"].keys()[0]
            self._collection = self._collections["collections"][self._collectionName]
            self._data = self._collection["data"]
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
            return self._data[index.row()][index.column()]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            row = index.row()
            col = index.column()
            self._data[row][col] = value
            if row >= self._maxRow:
                self._maxRow = row + 1
                self._collection["maxRow"] = self._maxRow
            if col >= self._maxColumn:
                self._maxColumn = col + 1
                self._collection["maxColumn"] = self._maxColumn
            # Emit dataChanged for both EditRole and DisplayRole
            self.dataChanged.emit(index, index, [Qt.EditRole, Qt.DisplayRole])
            self.save_to_file()
            return True
        return False

    @Slot(int)
    def addRows(self, count):
        if count <= 0:
            return
        new_row_count = self._rows_nb + count
        self.beginInsertRows(QModelIndex(), self._rows_nb, new_row_count - 1)
        self._rows_nb = new_row_count
        for _ in range(count):
            self._data.append([""] * self._columns_nb)
        self.endInsertRows()

    @Slot(int)
    def addColumns(self, count):
        if count <= 0:
            return
        new_col_count = self._columns_nb + count
        self.beginInsertColumns(QModelIndex(), self._columns_nb, new_col_count - 1)
        self._columns_nb = new_col_count
        for row in self._data:
            row.extend([""] * count)
        self.endInsertColumns()

    @Slot(int)
    def setRows(self, count):
        if count < 0:
            return
        if count < self._rows_nb:
            self.beginRemoveRows(QModelIndex(), count, self._rows_nb - 1)
            self._data = self._data[:count]
            self._rows_nb = count
            self.endRemoveRows()
        elif count > self._rows_nb:
            self.beginInsertRows(QModelIndex(), self._rows_nb, count - 1)
            for _ in range(count - self._rows_nb):
                self._data.append([""] * self._columns_nb)
            self._rows_nb = count
            self.endInsertRows()

    @Slot(int)
    def setColumns(self, count):
        if count < 0:
            return
        if count < self._columns_nb:
            self.beginRemoveColumns(QModelIndex(), count, self._columns_nb - 1)
            for row in self._data:
                row = row[:count]
            self._columns_nb = count
            self.endRemoveColumns()
        elif count > self._columns_nb:
            self.beginInsertColumns(QModelIndex(), self._columns_nb, count - 1)
            for row in self._data:
                row.extend([""] * (count - self._columns_nb))
            self._columns_nb = count
            self.endInsertColumns()

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
                "maxRow": self._maxRow,
                "maxColumn": self._maxColumn,
                "data": self._data,
            }
            self._collectionName = name
            self.save_to_file()
        else:
            print(f"Collection '{name}' already exists.")

    def save_to_file(self):
        """Save model data to a JSON file."""
        with open(f"data/general.json", "w") as f:
            json.dump(self._collections, f)
