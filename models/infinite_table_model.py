from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Property, Signal, Slot
from PySide6.QtGui import QColor
from utils.enums import Role
from ortools.sat.python import cp_model
from PyQt5.QtCore import QModelIndex, QVariant
import os
import json


class InfiniteTableModel(QAbstractTableModel):
    # Add QML-accessible signals
    columnColorChanged = Signal(int, QColor)
    
    def __init__(self, controller, collection_filename, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._data = {}
        self._column_role = {}
        self.collection_path = collection_filename+".json"
        self._used_row_count = max((row for row, col in self._data.keys()), default=0) + 1
        self._used_col_count = max((col for row, col in self._data.keys()), default=0) + 1
        self._row_count = self._used_row_count
        self._col_count = self._used_col_count
        self._hidden_row_at_start = 0  # Number of hidden rows at the start
        self._hidden_col_at_start = 0  # Number of hidden columns at the start
        self._role_colors = {
            Role.UNKNOWN: Qt.white,
            Role.CONDITION: Qt.cyan,
            Role.TAG: Qt.yellow,
            Role.NAME: Qt.green,
        }
        self.load_data()
        
        # Add QML-accessible properties
        self._role_colors = {
            Role.UNKNOWN: QColor("white"),
            Role.CONDITION: QColor("cyan"),
            Role.TAG: QColor("yellow"),
            Role.NAME: QColor("green"),
        }

    # Add QML-accessible properties
    @Property(QColor, constant=True)
    def conditionColor(self):
        return self._role_colors[Role.CONDITION]

    @Property(QColor, constant=True)
    def tagColor(self):
        return self._role_colors[Role.TAG]


    def load_data(self):
        if os.path.exists(self.collection_path):
            try:
                with open(self.collection_path, "r") as f:
                    loaded_data = json.load(f)
                
                # Load the main data
                self._data = {tuple(map(int, key.split(','))): value for key, value in loaded_data.get("data", {}).items()}
                
                # Load the column roles
                self._column_role = {int(col): Role(role) for col, role in loaded_data.get("column_roles", {}).items()}
                
            except Exception as e:
                print(f"Error loading {self.collection_path}: {e}")

    def save_data(self):
        # Convert tuple keys to string keys for JSON serialization.
        serializable_data = {
            "data": {f"{row},{col}": value for (row, col), value in self._data.items()},
            "column_roles": {str(col): role.value for col, role in self._column_role.items()}
        }
        try:
            with open(self.collection_path, "w") as f:
                json.dump(serializable_data, f)
        except Exception as e:
            print(f"Error saving {self.collection_path}: {e}")

    def rowCount(self, parent=QModelIndex()):
        return self._row_count

    def columnCount(self, parent=QModelIndex()):
        return self._col_count

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        row, col = index.row(), index.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._data.get((row, col), '')

        if role == Qt.BackgroundRole and row == 0:  # Apply color only to first row
            return QColor(self._role_colors.get(self._column_role.get(col, Role.UNKNOWN)))

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            if value == self._data.get((index.row(), index.column()), ''):
                return False
            self._data[index.row(), index.column()] = value
            self.save_data()
            if value:
                self._used_row_count = max(self._used_row_count, index.row() + 1)
                self._used_col_count = max(self._used_col_count, index.column() + 1)
            else:
                self._used_row_count = max((row for row, _ in self._data.keys()), default=0) + 1
                self._used_col_count = max((col for _, col in self._data.keys()), default=0) + 1
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False

    def change_column_color(self, col, role):
        """Set the background color of the first cell in the given column."""
        self._used_row_count = max(self._used_row_count, col + 1)
        if role == self._column_role.get(col, Role.UNKNOWN):
            return
        self._column_role[col] = role
        self.save_data()
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

    def roleNames(self):
        # Expose custom roles to QML
        roles = super().roleNames()
        roles[Qt.DisplayRole] = b"display"
        roles[Qt.BackgroundRole] = b"background"
        return roles

    def change_column_color(self, col, role):
        """QML-callable version"""
        self._column_role[col] = role
        self.save_data()
        self.columnColorChanged.emit(col, self._role_colors[role])