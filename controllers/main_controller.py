# controllers/main_controller.py

import sys
from PyQt5.QtWidgets import QApplication
from data.table_storage import TableStorage
from models.infinite_table_model import InfiniteTableModel
from views.spreadsheet_view import SpreadsheetView
from views.floating_button_panel import FloatingButtonPanel
from PyQt5.QtCore import QThread, pyqtSignal

class LoadRowsThread(QThread):
    finished = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model

    def run(self):
        self.model.load_more_rows()
        self.finished.emit()

class LoadColsThread(QThread):
    finished = pyqtSignal()

    def __init__(self, model):
        super().__init__()
        self.model = model

    def run(self):
        self.model.load_more_cols()
        self.finished.emit()

class MainController:
    """
    The Controller ties together the model(s) and view(s) and creates
    a floating button panel that can be dragged around.
    """
    def __init__(self, collection_filename):
        self.app = QApplication(sys.argv)
        self.storage = TableStorage(collection_filename)
        self.model = InfiniteTableModel(self.storage)
        self.view = SpreadsheetView(self)
        self.view.setModel(self.model)
        self.floating_panel = FloatingButtonPanel(self.view, self)
        self._position_floating_panel()

        # Thread management
        self.loading_rows = False
        self.loading_cols = False

    def load_more_rows(self):
        if not self.loading_rows:
            self.loading_rows = True
            self.thread = LoadRowsThread(self.model)
            self.thread.finished.connect(self.on_rows_loaded)
            self.thread.start()

    def on_rows_loaded(self):
        self.loading_rows = False
        self.thread.quit()
        self.thread.wait()

    def load_more_cols(self):
        if not self.loading_cols:
            self.loading_cols = True
            self.thread_col = LoadColsThread(self.model)
            self.thread_col.finished.connect(self.on_cols_loaded)
            self.thread_col.start()

    def on_cols_loaded(self):
        self.loading_cols = False
        self.thread_col.quit()
        self.thread_col.wait()

    def _position_floating_panel(self):
        parent = self.view
        vertical_sb = parent.verticalScrollBar()
        vertical_width = vertical_sb.width() if vertical_sb and vertical_sb.isVisible() else 0
        init_x = parent.width() - vertical_width - self.floating_panel.width()
        init_y = 0
        self.floating_panel.move(init_x, init_y)
        self.floating_panel.show()
    
    def get_model(self):
        return self.model

    def run(self):
        self.view.resize(1024, 768)  # This sets the normal geometry
        self.view.showMaximized()  # Changed from show()
        return self.app.exec_()

    def load_more_rows(self):
        self.model.load_more_rows()
    
    def load_more_cols(self):
        self.model.load_more_cols()

    def load_less_rows(self, last_visible_row):
        self.model.load_less_rows(last_visible_row)
    
    def load_less_cols(self, last_visible_col):
        self.model.load_less_cols(last_visible_col)