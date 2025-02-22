from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor

class InfiniteTableModel(QAbstractTableModel):
    """
    A QAbstractTableModel that dynamically expands and contracts based on user scrolling.
    """
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self._storage = storage
        self._used_row_count = max((row for row, col in self._storage._data.keys()), default=0) + 1
        self._used_col_count = max((col for row, col in self._storage._data.keys()), default=0) + 1
        self._row_count = self._used_row_count
        self._col_count = self._used_col_count
        self._hidden_row_at_start = 0  # Number of hidden rows at the start
        self._hidden_col_at_start = 0  # Number of hidden columns at the start
        self._column_colors = {}  # Store column background colors

    def rowCount(self, parent=QModelIndex()):
        return self._row_count

    def columnCount(self, parent=QModelIndex()):
        return self._col_count

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row, col = index.row(), index.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._storage.get_value(row, col)

        if role == Qt.BackgroundRole and row == 0:  # Apply color only to first row
            return QColor(self._column_colors.get(col, Qt.white))

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            self._storage.set_value(index.row(), index.column(), value)
            if value:
                self._used_row_count = max(self._used_row_count, index.row() + 1)
                self._used_col_count = max(self._used_col_count, index.column() + 1)
            else:
                self._used_row_count = max((row for row, col in self._storage._data.keys()), default=0) + 1
                self._used_col_count = max((col for row, col in self._storage._data.keys()), default=0) + 1
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def set_column_color(self, col, color):
        """Set the background color of the first cell in the given column."""
        self._column_colors[col] = color
        index = self.index(0, col)  # First row, specified column
        self.dataChanged.emit(index, index, [Qt.BackgroundRole])
    
    def load_more_rows(self):
        self.beginResetModel()
        self._row_count += 1
        self.endResetModel()
    
    def load_more_cols(self):
        self.beginResetModel()
        self._col_count += 1
        self.endResetModel()
    
    def load_less_rows(self, last_visible_row):
        if last_visible_row >= self._row_count - 1:
            return
        self.beginResetModel()
        self._row_count = max(last_visible_row + 1, self._used_row_count)
        self.endResetModel()
    
    def load_less_cols(self, last_visible_col):
        if last_visible_col >= self._col_count - 1:
            return
        self.beginResetModel()
        self._col_count = max(last_visible_col + 1, self._used_col_count)
        self.endResetModel()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
