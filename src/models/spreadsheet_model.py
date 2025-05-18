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
from PySide6.QtGui import QFont, QFontMetrics
from models.generate_sortings import find_valid_sortings
import threading


class SpreadsheetModel(QAbstractTableModel):
    signal = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.default_width = 100
        self.horizontal_padding = 5
        self.vertical_padding = 5
        self.font = QFont("Arial", 10)

        self.metrics = QFontMetrics(self.font)
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
        
        table = [[] for i in range(50)]
        table[0] = ["after 1", "as far as possible from 1"]
        thread = threading.Thread(target=self.compute_and_print_sorting, args=(table,))
        thread.start()
    
    def compute_and_print_sorting(self, table):
        sorting = find_valid_sortings(table)
        print("Sorting result:", sorting)
    
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
        if 0 <= column < self._maxColumn:
            prevWidth = self._columnWidths[column - 1] if column > 0 else 0
            return self._columnWidths[column] - prevWidth
        return self.default_width + self.horizontal_padding * 2

    @Slot(int, result=int)
    def rowHeight(self, row):
        if 0 <= row < self._maxRow:
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
            self.signal.emit({"type": "input_text_changed", "value": self._collectionName})
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
            self._maxRow = self._collection["maxRow"]
            self._maxColumn = self._collection["maxColumn"]
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
        return int(self._columns_nb)

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
                    prevHeight = self._rowHeights[r - 1] if r > 0 else 0
                    self._rowHeights.append(prevHeight + self.rowHeight(-1))
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
                    prevWidth = self._columnWidths[col - 1] if col > 0 else 0
                    self._columnWidths.append(self.columnWidth(-1) - prevWidth)
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
            self.verticalScroll(self._verticalScrollPosition, self._verticalScrollSize, self._tableViewContentY, self._tableViewHeight)
            self.horizontalScroll(self._horizontalScrollPosition, self._horizontalScrollSize, self._tableViewContentX, self._tableViewWidth)
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
        if position >= 1.0 - size and not start:
            self.addRows(1)
        else:
            sizeToReach = tableViewContentY + tableViewHeight
            if self._maxRow and sizeToReach < self._rowHeights[-1]:
                lowerBound = 0
                upperBound = self._maxRow
                while lowerBound < upperBound:
                    mid = (lowerBound + upperBound) // 2
                    if self._rowHeights[mid] < sizeToReach:
                        lowerBound = mid + 1
                    else:
                        upperBound = mid
                requiredRows = lowerBound
            else:
                prevHeight = self._rowHeights[-1] if self._maxRow > 0 else 0
                requiredRows = self._maxRow + (sizeToReach - prevHeight) // self.rowHeight(-1) + 1
            currentRows = self.rowCount()
            if requiredRows != currentRows:
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
            if self._maxColumn and sizeToReach < self._columnWidths[-1]:
                lowerBound = 0
                upperBound = self._maxColumn
                while lowerBound < upperBound:
                    mid = (lowerBound + upperBound) // 2
                    if self._columnWidths[mid] < sizeToReach:
                        lowerBound = mid + 1
                    else:
                        upperBound = mid
                requiredColumns = lowerBound
            else:
                prevWidth = self._columnWidths[-1] if self._maxColumn > 0 else 0
                requiredColumns = self._maxColumn + (sizeToReach - prevWidth) // self.columnWidth(-1) + 1
            currentColumns = self.columnCount()
            if requiredColumns != currentColumns:
                self.setColumns(requiredColumns)

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
