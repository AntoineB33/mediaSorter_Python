import sys
import json
from PySide6.QtCore import QAbstractTableModel, Qt, QUrl, QModelIndex, Slot, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

class SpreadsheetModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.c = False
        self._data = []
        self._rows_nb = 0
        self._columns_nb = 0
        self._used_rows_nb = -1  # Track the highest edited row index
        self._used_cols_nb = -1  # Track the highest edited column index
        self.load_from_file()

    def rowCount(self, parent=None):
        return self._rows_nb

    def columnCount(self, parent=None):
        return self._columns_nb
    
    @Slot(result=int)
    def get_used_rows_nb(self):
        return self._used_rows_nb
    
    @Slot(result=int)
    def get_used_cols_nb(self):
        return self._used_cols_nb

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.isValid():
            return self._data[index.row()][index.column()]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            row = index.row()
            col = index.column()
            self._data[row][col] = value
            if row > self._used_rows_nb:
                self._used_rows_nb = row
            if col > self._used_cols_nb:
                self._used_cols_nb = col
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
        if count < 0 or self.c:
            return
        # self.c = True
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
        return self._used_rows_nb

    @Slot(result=int)
    def getMaxColumn(self):
        return self._used_cols_nb

    def roleNames(self):
        return {Qt.DisplayRole: b"display"}
    
    def save_to_file(self, filename=r"data\spreadsheets\spreadsheet.json"):
        """Save model data to a JSON file"""
        data = {
            "max_row": self._used_rows_nb,
            "max_col": self._used_cols_nb,
            "data": self._data
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load_from_file(self, filename="spreadsheet.json"):
        """Load model data from a JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.beginResetModel()
            self._used_rows_nb = data["max_row"]
            self._used_cols_nb = data["max_col"]
            self._data = data["data"]
            self.endResetModel()
        except FileNotFoundError:
            # No saved data, initialize with defaults if needed
            pass
        except Exception as e:
            print(f"Error loading spreadsheet: {str(e)}")