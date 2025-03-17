# main.py
import sys
from PySide6.QtCore import QAbstractTableModel, Qt, QUrl, QModelIndex, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

class SpreadsheetModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows = 0
        self._columns = 0
        self._data = []

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
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
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

    def roleNames(self):
        return {Qt.DisplayRole: b"display"}

def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    model = SpreadsheetModel()
    engine.rootContext().setContextProperty("spreadsheetModel", model)
    
    engine.load(QUrl.fromLocalFile("main.qml"))
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()