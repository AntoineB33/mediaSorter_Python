import sys
import json
from pathlib import Path
from math import floor
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
    input_text_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cellHorizPadding = 2
        self._cellVertPadding = 2
        self._textWidth = 36
        self._textHeight = 16
        self._rows_nb = 0
        self._columns_nb = 0
        self._collections = {
            "collections": {},
        }
        self._collectionName = self.getDefaultSpreadsheetName()
        self._data = []
        self._rowHeights = []
        self._colWidths = []
        self._maxRow = 0
        self._maxColumn = 0
        self._collection = {"data": [], "rowHeights": [], "colWidths": [], "maxRow": 0, "maxColumn": 0}
        self._collections = {
            "collections": {self._collectionName: self._collection},
            "collectionName": self._collectionName,
        }
        try:
            Path("data").mkdir(parents=True, exist_ok=True)
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
                self._colWidths = self._collection["colWidths"]
                self._maxRow = self._collection["maxRow"]
                self._maxColumn = self._collection["maxColumn"]
        except FileNotFoundError:
            # No saved data, initialize with defaults if needed
            pass
        except Exception as e:
            print(f"Error loading spreadsheet: {str(e)}")
        self.input_text_changed.emit()
    
    @Property(str, notify=input_text_changed)
    def input_text(self):
        """Property for the input text."""
        return self._collectionName

    @Slot(result=str)
    def getCollectionName(self):
        """Return the current collection name."""
        return self._collectionName

    @Slot(int, result=int)
    def rowHeight(self, row):
        """Return the height of a row."""
        if row >= self._maxColumn:
            previous_height = self._rowHeights[self._maxColumn - 1] if self._maxColumn > 0 else 0
            return previous_height + (row - self._maxColumn) * (self._cellVertPadding * 2 + self._textHeight)
        return self._rowHeights[row]

    @Slot(int, result=int)
    def getRenderRowCount(self, height):
        """Return the number of rows that can be rendered in the given height."""
        if height <= 0:
            return 0
        row_count = 0
        for i in range(self._maxRow):
            row_count += self._rowHeights[i] + self._cellVertPadding * 2 + self._textHeight
            if row_count > height:
                return i + 1
        return self._maxRow + floor(1 + (height - row_count) / (self._cellVertPadding * 2 + self._textHeight))

    @Slot(result=str)
    def getDefaultSpreadsheetName(self, base_name = "Default"):
        """Generate a default spreadsheet name not already used."""
        i = 1
        while f"{base_name}_{i}" in self._collections["collections"]:
            i += 1
        return f"{base_name}_{i}"

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
        # self._collectionName = "name"
        # self.input_text_changed.emit()
        # return
        self.beginResetModel()
        if new_collection_name := (name in self._collections["collections"]):
            name = self.getDefaultSpreadsheetName(name)
        self._collections["collections"][name] = {
            "data": [],
            "rowHeights": [],
            "colWidths": [],
            "maxRow": 0,
            "maxColumn": 0,
        }
        self._collectionName = name
        self._collection = self._collections["collections"][name]
        self._data = self._collection["data"]
        self._rowHeights = self._collection["rowHeights"]
        self._colWidths = self._collection["colWidths"]
        self._maxRow = self._collection["maxRow"]
        self._maxColumn = self._collection["maxColumn"]
        self.endResetModel()
        if new_collection_name:
            self.input_text_changed.emit()
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
                        "colWidths": [],
                        "maxRow": 0,
                        "maxColumn": 0,
                    }
                }
            self._collectionName = self._collections["collections"].keys()[0]
            self._collection = self._collections["collections"][self._collectionName]
            self._data = self._collection["data"]
            self._rowHeights = self._collection["rowHeights"]
            self._colWidths = self._collection["colWidths"]
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
            self._colWidths = self._collection["colWidths"]
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
            if index.row() < len(self._data) and index.column() < len(self._data[index.row()]):
                return self._data[index.row()][index.column()]
            else:
                return ""
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            row = index.row()
            col = index.column()
            self.beginResetModel()
            if value:
                if row >= self._maxRow:
                    for i in range(row - self._maxRow + 1):
                        self._data.append([""] * self._maxColumn)
                        previous_height = self._rowHeights[-1] if self._maxRow > 0 else 0
                        self._rowHeights.append(previous_height + self._cellVertPadding * 2 + self._textHeight)
                    self._maxRow = row + 1
                    self._collection["maxRow"] = self._maxRow
                if col >= self._maxColumn:
                    for aRow in self._data:
                        aRow.extend([""] * (col - self._maxColumn + 1))
                    for i in range(col - self._maxColumn + 1):
                        previous_width = self._colWidths[-1] if self._maxColumn > 0 else 0
                        self._colWidths.append(previous_width + self._rowWidth
                    self._maxColumn = col + 1
                    self._collection["maxColumn"] = self._maxColumn
                self._data[row][col] = value
            elif row < self._maxRow and col < self._maxColumn:
                self._data[row][col] = ""
                if row == self._maxRow - 1:
                    for i in range(self._maxRow - 1, -1, -1):
                        if self._data[i].count("") == self._maxColumn:
                            self._data.pop(i)
                            self._rowHeights.pop(i)
                            self._maxRow -= 1
                            self._collection["maxRow"] = self._maxRow
                        else:
                            break
                if col == self._maxColumn - 1:
                    for i in range(self._maxColumn - 1, -1, -1):
                        if all(aRow[i] == "" for aRow in self._data):
                            self._maxColumn -= 1
                            self._collection["maxColumn"] = self._maxColumn
                            for aRow in self._data:
                                aRow.pop(i)
                        else:
                            break
            if row < self._maxColumn:
                previous_height = self._rowHeights[row - 1] if row > 0 else 0
                height_diff = previous_height + self._cellVertPadding * 2 + self._textHeight * value.count("\n") - self._rowHeights[row]
                if height_diff:
                    for i in range(row, self._maxColumn):
                        self._rowHeights[i] += height_diff
            self.endResetModel()
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
        self.endInsertRows()

    @Slot(int)
    def addColumns(self, count):
        if count <= 0:
            return
        new_col_count = self._columns_nb + count
        self.beginInsertColumns(QModelIndex(), self._columns_nb, new_col_count - 1)
        self._columns_nb = new_col_count
        self.endInsertColumns()

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
            self.beginResetModel()
            self._collections["collections"][name] = {
                "data": self._data,
                "_rowHeights": self._rowHeights,
                "maxRow": self._maxRow,
                "maxColumn": self._maxColumn,
            }
            del self._collections["collections"][self._collectionName]
            self._collectionName = name
            self.endResetModel()
            self.input_text_changed.emit()
            self.save_to_file()
        else:
            print(f"Collection name '{name}' already exists. Please choose a different name.")

    def save_to_file(self):
        """Save model data to a JSON file."""
        with open(f"data/general.json", "w") as f:
            json.dump(self._collections, f)