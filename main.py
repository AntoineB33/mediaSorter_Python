import sys
from PySide6.QtCore import Qt, QAbstractTableModel, Signal, QModelIndex, Property, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

class SpreadsheetModel(QAbstractTableModel):
    column_width_changed = Signal(int)

    def __init__(self, rows=10, columns=10):
        super().__init__()
        self._data = [[f"Row {i+1}, Col {j+1}" for j in range(columns)] for i in range(rows)]
        self._column_widths = [100] * columns  # Initial width 100

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        return self._data[index.row()][index.column()]

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole and index.isValid():
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable
    
    @Property(int, constant=True)
    def column_count(self):
        return self.columnCount()

    @Slot(int, result=int)
    def columnWidth(self, column):
        return self._column_widths[column] if 0 <= column < len(self._column_widths) else 100

    @Slot(int, int)
    def updateColumnWidth(self, column, new_width):
        if 0 <= column < len(self._column_widths) and new_width > self._column_widths[column]:
            self._column_widths[column] = new_width
            self.column_width_changed.emit(column)

    @Slot(int, int, str)
    def setCellData(self, row, column, value):
        index = self.index(row, column)
        self.setData(index, value, Qt.EditRole)

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    model = SpreadsheetModel()
    engine.rootContext().setContextProperty("spreadsheetModel", model)
    
    engine.load("main.qml")
    
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())