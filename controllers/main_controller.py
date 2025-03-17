from PySide6.QtCore import QObject, Slot, Signal, QThread
from models.infinite_table_model import InfiniteTableModel

class LoadThread(QThread):
    finished = Signal()
    
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task

    def run(self):
        self.task()
        self.finished.emit()

class MainController(QObject):
    # Signals for QML communication
    modelAboutToChange = Signal()
    modelChanged = Signal()
    columnColorChanged = Signal(int, str)  # (column, colorName)
    
    def __init__(self, collection_filename):
        super().__init__()
        self._model = InfiniteTableModel(self, collection_filename)
        self._loading = False
        
        # Connect model signals
        self._model.columnColorChanged.connect(self.handle_column_color_change)

    @property
    def model(self):
        return self._model

    # QML-exposed methods
    @Slot()
    def load_more_rows(self):
        if not self._loading:
            self._loading = True
            self.thread = LoadThread(self._model.load_more_rows)
            self.thread.finished.connect(self.on_load_finished)
            self.thread.start()

    @Slot(int)
    def load_less_rows(self, last_visible_row):
        self.modelAboutToChange.emit()
        self._model.load_less_rows(last_visible_row)
        self.modelChanged.emit()

    @Slot(int, int)
    def change_column_color(self, column, role_index):
        roles = [Role.UNKNOWN, Role.CONDITION, Role.TAG, Role.NAME]
        self._model.change_column_color(column, roles[role_index])

    @Slot()
    def sort_data(self):
        self.modelAboutToChange.emit()
        self._model.sort_data()
        self.modelChanged.emit()

    @Slot(int, int)
    def handle_scroll(self, position, maximum):
        if position >= maximum - 100:  # 100px threshold
            self.load_more_rows()

    def handle_column_color_change(self, col, color):
        self.columnColorChanged.emit(col, color.name())

    @Slot()
    def on_load_finished(self):
        self._loading = False
        self.modelChanged.emit()
        self.thread.quit()
        self.thread.wait()

    # QML-accessible properties
    @Property(bool, constant=True)
    def isLoading(self):
        return self._loading