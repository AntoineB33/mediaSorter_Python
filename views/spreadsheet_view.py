from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView

class SpreadsheetView(QTableView):
    """
    A QTableView that dynamically adjusts row and column counts based on scrolling and window resizing.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller  # Use controller instead of calling the model directly
        self.setModel(controller.get_model())  # Set the model via the controller
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        # Initialize the frozen row view
        self.init_frozen_row()

        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self.handle_vertical_scroll)
        self.horizontalScrollBar().valueChanged.connect(self.handle_horizontal_scroll)

    def init_frozen_row(self):
        # Create a frozen row view
        self.frozen_row_view = QTableView(self)
        self.frozen_row_view.setModel(self.model())
        self.frozen_row_view.setFocusPolicy(Qt.NoFocus)
        self.frozen_row_view.verticalHeader().hide()
        self.frozen_row_view.horizontalHeader().hide()
        self.frozen_row_view.setStyleSheet("QTableView { border: none; }")
        self.frozen_row_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.frozen_row_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Synchronize horizontal scrolling with main view
        self.horizontalScrollBar().valueChanged.connect(
            self.frozen_row_view.horizontalScrollBar().setValue
        )
        
        # Synchronize column widths
        self.horizontalHeader().sectionResized.connect(self.update_frozen_column_width)
        
        # Make frozen view ignore mouse events
        self.frozen_row_view.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        # Ensure column widths match initially
        self.sync_frozen_column_widths()
        
        # Initial geometry update
        self.update_frozen_view_geometry()
        
        # Update when row 0 is resized
        self.verticalHeader().sectionResized.connect(self.on_row_resized)

    def sync_frozen_column_widths(self):
        """Ensure frozen row column widths match main table."""
        for col in range(self.model().columnCount()):
            self.frozen_row_view.setColumnWidth(col, self.columnWidth(col))


    def update_frozen_view_geometry(self):
        if self.model().rowCount() == 0:
            self.frozen_row_view.hide()
            return

        hheader_height = self.horizontalHeader().height()
        vheader_width = self.verticalHeader().width()  # Get the width of the row numeration
        self.frozen_row_view.move(vheader_width, hheader_height)  # Align properly
        
        self.frozen_row_view.setFixedWidth(self.viewport().width())
        
        # Set height to row 0's height
        row0_height = self.rowHeight(0)
        self.frozen_row_view.setFixedHeight(row0_height)
        self.frozen_row_view.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_row_count(self.verticalScrollBar().value())
        self.adjust_col_count(self.horizontalScrollBar().value())

        # Ensure frozen row aligns with main table's data area
        self.sync_frozen_column_widths()
        self.update_frozen_view_geometry()


    def on_row_resized(self, row, old_height, new_height):
        if row == 0:
            self.frozen_row_view.setFixedHeight(new_height)
            self.update_frozen_view_geometry()

    def update_frozen_column_width(self, logical_index, old_size, new_size):
        """Ensure that when a column is resized in the main table, it resizes in the frozen row view too."""
        self.frozen_row_view.setColumnWidth(logical_index, new_size)


    def handle_vertical_scroll(self, value):
        self.adjust_row_count(value)

    def handle_horizontal_scroll(self, value):
        self.frozen_row_view.horizontalScrollBar().setValue(value)
        self.adjust_col_count(value)
    
    def adjust_row_count(self, value):
        if value == self.verticalScrollBar().maximum():
            self.controller.load_more_rows()
        else:
            lastRow = self.rowAt(self.viewport().height() - 1)
            self.controller.load_less_rows(lastRow)
    
    def adjust_col_count(self, value):
        if value == self.horizontalScrollBar().maximum():
            self.controller.load_more_cols()
        else:
            lastCol = self.columnAt(self.viewport().width() - 1)
            self.controller.load_less_cols(lastCol)
    