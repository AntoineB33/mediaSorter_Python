import sys
import json
from PySide6.QtCore import QAbstractTableModel, Qt, QUrl, QModelIndex, Slot, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

class SpreadsheetModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows = 0
        self._columns = 0
        self._data = []
        self._max_row = -1  # Track the highest edited row index
        self._max_col = -1  # Track the highest edited column index
        self.load_from_file()

    def rowCount(self, parent=None):
        return self._rows

    def columnCount(self, parent=None):
        return self._columns

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.isValid():
            return self._data[index.row()][index.column()]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            row = index.row()
            col = index.column()
            self._data[row][col] = value
            if row > self._max_row:
                self._max_row = row
            if col > self._max_col:
                self._max_col = col
            # Emit dataChanged for both EditRole and DisplayRole
            self.dataChanged.emit(index, index, [Qt.EditRole, Qt.DisplayRole])
            return True
        return False

    @Slot(int)
    def addRows(self, count):
        if count <= 0:
            return
        new_row_count = self._rows + count
        self.beginInsertRows(QModelIndex(), self._rows, new_row_count - 1)
        self._rows = new_row_count
        for _ in range(count):
            self._data.append([""] * self._columns)
        self.endInsertRows()

    @Slot(int)
    def addColumns(self, count):
        if count <= 0:
            return
        new_col_count = self._columns + count
        self.beginInsertColumns(QModelIndex(), self._columns, new_col_count - 1)
        self._columns = new_col_count
        for row in self._data:
            row.extend([""] * count)
        self.endInsertColumns()
    
    @Slot(int)
    def setRows(self, count):
        if count < 0:
            return
        if count < self._rows:
            self.beginRemoveRows(QModelIndex(), count, self._rows - 1)
            self._data = self._data[:count]
            self._rows = count
            self.endRemoveRows()
        elif count > self._rows:
            self.beginInsertRows(QModelIndex(), self._rows, count - 1)
            for _ in range(count - self._rows):
                self._data.append([""] * self._columns)
            self._rows = count
            self.endInsertRows()
    
    @Slot(int)
    def setColumns(self, count):
        if count < 0:
            return
        if count < self._columns:
            self.beginRemoveColumns(QModelIndex(), count, self._columns - 1)
            for row in self._data:
                row = row[:count]
            self._columns = count
            self.endRemoveColumns()
        elif count > self._columns:
            self.beginInsertColumns(QModelIndex(), self._columns, count - 1)
            for row in self._data:
                row.extend([""] * (count - self._columns))
            self._columns = count
            self.endInsertColumns()

    @Slot(result=int)
    def getMaxRow(self):
        return self._max_row

    @Slot(result=int)
    def getMaxColumn(self):
        return self._max_col

    def roleNames(self):
        return {Qt.DisplayRole: b"display"}
    
    def save_to_file(self, filename="spreadsheet.json"):
        """Save model data to a JSON file"""
        data = {
            "rows": self._rows,
            "columns": self._columns,
            "max_row": self._max_row,
            "max_col": self._max_col,
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
            self._rows = data["rows"]
            self._columns = data["columns"]
            self._max_row = data["max_row"]
            self._max_col = data["max_col"]
            self._data = data["data"]
            self.endResetModel()
        except FileNotFoundError:
            # No saved data, initialize with defaults if needed
            pass
        except Exception as e:
            print(f"Error loading spreadsheet: {str(e)}")

def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    model = SpreadsheetModel()
    engine.rootContext().setContextProperty("spreadsheetModel", model)
    
    # Save data when app quits
    app.aboutToQuit.connect(model.save_to_file)
    
    engine.load(QUrl.fromLocalFile("main.qml"))
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()