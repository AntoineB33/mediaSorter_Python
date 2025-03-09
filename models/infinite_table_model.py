from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor
from utils.enums import Role
from ortools.sat.python import cp_model
from PyQt5.QtCore import QModelIndex, QVariant

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
        self._column_role = {}  # Store column roles
        self._role_colors = {
            Role.UNKNOWN: Qt.white,
            Role.CONDITION: Qt.cyan,
            Role.TAG: Qt.yellow,
            Role.NAME: Qt.green,
        }

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
            return QColor(self._role_colors.get(self._column_role.get(col, Role.UNKNOWN)))

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

    def set_column_color(self, col, role):
        """Set the background color of the first cell in the given column."""
        self._used_row_count = max(self._used_row_count, col + 1)
        self._column_role[col] = role
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

    def sort_data(self):
        """Sorts the rows based on constraints from Role.CONDITION columns, tags from Role.TAG, and names from Role.NAME."""
        # Collect all objects (rows) with their attributes
        objects = []
        for row in range(self._used_row_count):
            obj = {
                'name': '',
                'tags': [],
                'conditions': [],
                'original_row': row
            }
            for col in range(self._used_col_count):
                role = self._column_role.get(col, Role.UNKNOWN)
                value = self._storage.get_value(row, col)
                if role == Role.NAME:
                    obj['name'] = value
                elif role == Role.TAG:
                    if value:  # Assume tags are stored as strings (split if multiple)
                        obj['tags'].extend(value.split(','))
                elif role == Role.CONDITION:
                    if value:
                        obj['conditions'].append(value)
            objects.append(obj)
        
        # Parse conditions into hard constraints and optimization goals
        # Example: Extract "A before B" constraints and "maximize distance D" goals
        constraints = []
        a_tag_objects = []  # Objects with tag "A"
        b_tag_objects = []  # Objects with tag "B"
        d_tag_objects = []  # Objects with tag "D"
        for obj in objects:
            for condition in obj['conditions']:
                # Simple parser for demonstration (customize based on your condition format)
                if "before" in condition:
                    parts = condition.split()
                    tag = parts[0]
                    other_tag = parts[2]
                    if tag == 'A':
                        a_tag_objects.append(obj)
                    elif other_tag == 'B':
                        b_tag_objects.append(obj)
                elif "maximize distance" in condition:
                    target_tag = condition.split()[-1]
                    if target_tag == 'D':
                        d_tag_objects = [obj for obj in objects if target_tag in obj['tags']]
        
        # Set up CP-SAT model
        model = cp_model.CpModel()
        num_objects = len(objects)
        positions = {obj['original_row']: model.NewIntVar(0, num_objects - 1, f'pos_{obj["original_row"]}') for obj in objects}
        model.AddAllDifferent(list(positions.values()))  # All positions must be unique
        
        # Hard constraint: All "A" tagged objects before "B" tagged
        for a_obj in a_tag_objects:
            for b_obj in b_tag_objects:
                model.Add(positions[a_obj['original_row']] < positions[b_obj['original_row']])
        
        # Soft constraint: Maximize minimum distance between "D" tagged objects
        if d_tag_objects:
            d_pairs = [(d1, d2) for i, d1 in enumerate(d_tag_objects) for d2 in d_tag_objects[i+1:]]
            dist_vars = []
            for d1, d2 in d_pairs:
                diff = model.NewIntVar(-num_objects, num_objects, '')
                model.Add(diff == positions[d1['original_row']] - positions[d2['original_row']])
                dist_var = model.NewIntVar(0, num_objects, '')
                model.AddAbsEquality(dist_var, diff)
                dist_vars.append(dist_var)
            if dist_vars:
                min_distance = model.NewIntVar(0, num_objects, 'min_distance')
                model.AddMinEquality(min_distance, dist_vars)
                model.Maximize(min_distance)
        
        # Solve the model
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract sorted order
            sorted_objects = sorted(objects, key=lambda x: solver.Value(positions[x['original_row']]))
            sorted_order = [obj['original_row'] for obj in sorted_objects]
            
            # Reorder the storage's data
            new_data = {}
            for new_row, old_row in enumerate(sorted_order):
                for col in range(self._used_col_count):
                    key = (old_row, col)
                    if key in self._storage._data:
                        new_data[(new_row, col)] = self._storage._data[key]
            self._storage._data = new_data
            
            # Update used row count and notify view
            self._used_row_count = num_objects
            self.beginResetModel()
            self.endResetModel()
        else:
            print("Sorting failed: No valid order found.")