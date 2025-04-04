import sys
import json
from pathlib import Path
from PySide6.QtCore import QAbstractTableModel, Qt, QUrl, QModelIndex, Slot, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

class SpreadsheetModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []
        self._rows_nb = 0
        self._columns_nb = 0
        self.collectionName = "collection_1"
        self._maxRow = 0
        self._maxColumn = 0
        self._collection = {"maxRow": self._maxRow, "maxColumn": self._maxColumn, "data": self._data}
        self._collections = {"data": {self.collectionName: self._collection}, "collectionName": self.collectionName}
        self.load_from_file()

    @Slot(result=str)
    def getDefaultSpreadsheetName(self):
        """Generate a default spreadsheet name not already used."""
        existing_names = self.getSpreadsheetNames()
        i = 1
        while f"Default_{i}" in existing_names:
            i += 1
        return f"Default_{i}"

    @Slot(result=list)
    def getSpreadsheetNames(self):
        """Return a list of saved spreadsheet names."""
        try:
            return [f.stem for f in Path("data/spreadsheets").glob("*.json")]
        except Exception as e:
            print(f"Error fetching spreadsheet names: {str(e)}")
            return []

    @Slot(str)
    def setSpreadsheetName(self, name):
        """Set the current spreadsheet name."""
        self.collectionName = name
        self.save_to_file()

    @Slot(str)
    def loadSpreadsheet(self, name):
        """Load a spreadsheet by name."""
        self.collectionName = name
        self.load_from_file(f"data/spreadsheets/{name}.json")

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

    @Slot(result=list)
    def getExistingCollectionNames(self):
        """Return a list of existing collection names."""
        return list(self._collections["data"].keys())
    
    def save_to_file(self, filename=None):
        """Save model data to a JSON file."""
        if not filename:
            filename = f"data/spreadsheets/{self.collectionName}.json"
        Path("data/spreadsheets").mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self._collections, f)

    def load_from_file(self, filename=None):
        """Load model data from a JSON file."""
        if not filename:
            filename = f"data/spreadsheets/{self.collectionName}.json"
        try:
            with open(filename, 'r') as f:
                collections = json.load(f)
            
            if collections:
                self.beginResetModel()
                self._collections = collections
                self._collectionName = self._collections["collectionName"]
                self._collection = self._collections["data"][self._collectionName]
                self._data = self._collection["data"]
                self._maxRow = self._collection["maxRow"]
                self._maxColumn = self._collection["maxColumn"]
                self.endResetModel()
        except FileNotFoundError:
            # No saved data, initialize with defaults if needed
            pass
        except Exception as e:
            print(f"Error loading spreadsheet: {str(e)}")