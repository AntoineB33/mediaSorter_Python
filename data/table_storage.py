# data/table_storage.py

import json
import os

class TableStorage:
    """
    A simple class to store table data in a dictionary keyed by (row, col).
    It automatically loads data from a file and saves data each time a cell is edited.
    """
    def __init__(self, filename):
        self.filename = os.path.join("data", "saves", filename)
        self._data = {}
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    loaded_data = json.load(f)
                # Convert string keys (e.g., "1,2") back to tuple (1, 2)
                self._data = {tuple(map(int, key.split(','))): value for key, value in loaded_data.items()}
            except Exception as e:
                print(f"Error loading {self.filename}: {e}")

    def save_data(self):
        # Convert tuple keys to string keys for JSON serialization.
        serializable_data = {f"{row},{col}": value for (row, col), value in self._data.items()}
        try:
            with open(self.filename, "w") as f:
                json.dump(serializable_data, f)
        except Exception as e:
            print(f"Error saving {self.filename}: {e}")

    def get_value(self, row, col):
        return self._data.get((row, col), "")

    def set_value(self, row, col, value):
        self._data[(row, col)] = value
        # Save immediately after editing a cell.
        self.save_data()
        
