from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtCore import Qt, QModelIndex, QEvent
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import QEvent, Qt, QSize
from PyQt5.QtCore import QTimer

class SpreadsheetView(QTableView):
    """
    A QTableView with a frozen first row (including vertical header) that is fully editable.
    """
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.default_size = QSize(1024, 768)  # Match controller size
        self.setModel(controller.get_model())
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.init_frozen_row()

        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self.handle_vertical_scroll)
        self.horizontalScrollBar().valueChanged.connect(self.handle_horizontal_scroll)

        # Update frozen view on model changes
        self.model().rowsInserted.connect(self.update_frozen_view_geometry)
        self.model().rowsRemoved.connect(self.update_frozen_view_geometry)
        
        self.scroll_timer = QTimer()
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.timeout.connect(self.adjust_after_scroll)
        self.last_vertical_value = 0
        self.last_horizontal_value = 0

    def handle_vertical_scroll(self, value):
        self.last_vertical_value = value
        self.scroll_timer.start(200)  # Adjust delay as needed

    def handle_horizontal_scroll(self, value):
        self.last_horizontal_value = value
        self.scroll_timer.start(200)

    def adjust_after_scroll(self):
        self.adjust_row_count(self.last_vertical_value)
        self.adjust_col_count(self.last_horizontal_value)
        self.frozen_row_view.verticalScrollBar().setValue(0)
        self.frozen_row_view.horizontalScrollBar().setValue(self.last_horizontal_value)

    def init_frozen_row(self):
        self.frozen_row_view = QTableView(self)
        self.frozen_row_view.setModel(self.model())
        self.frozen_row_view.setFocusPolicy(Qt.StrongFocus)
        self.frozen_row_view.horizontalHeader().hide()
        self.frozen_row_view.setStyleSheet("QTableView { border: none; }")
        self.frozen_row_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.frozen_row_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Show vertical header and use independent selection model
        self.frozen_row_view.verticalHeader().show()
        
        # Sync horizontal scroll and column widths
        self.horizontalScrollBar().valueChanged.connect(
            self.frozen_row_view.horizontalScrollBar().setValue
        )
        self.horizontalHeader().sectionResized.connect(self.update_frozen_column_width)
        
        self.sync_frozen_column_widths()
        self.update_frozen_view_geometry()
        self.verticalHeader().sectionResized.connect(self.on_row_resized)

        # Install event filter to handle mouse events in frozen view
        self.frozen_row_view.viewport().installEventFilter(self)
        self.frozen_row_view.verticalHeader().viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if (source == self.frozen_row_view.viewport() or 
            source == self.frozen_row_view.verticalHeader().viewport()):
            if event.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick]:
                # Get index from frozen view's coordinates
                if source == self.frozen_row_view.verticalHeader().viewport():
                    # Handle vertical header click (row 0)
                    row = 0
                    col = self.columnAt(event.x() + self.verticalHeader().width())  # Adjust for header width
                    index = self.model().index(row, col)
                else:
                    # Handle cell click
                    index = self.frozen_row_view.indexAt(event.pos())
                
                if index.isValid():
                    # Edit directly in frozen view
                    self.frozen_row_view.setCurrentIndex(index)
                    self.frozen_row_view.edit(index)
                    return True
        return super().eventFilter(source, event)

    def sync_frozen_column_widths(self):
        for col in range(self.model().columnCount()):
            self.frozen_row_view.setColumnWidth(col, self.columnWidth(col))

    def update_frozen_view_geometry(self):
        if self.model().rowCount() == 0:
            self.frozen_row_view.hide()
            return

        hheader_height = self.horizontalHeader().height()
        vheader_width = self.verticalHeader().width()
        viewport_width = self.viewport().width()
        row0_height = self.rowHeight(0)

        # Position frozen view to cover vertical header and first row cells
        self.frozen_row_view.move(0, hheader_height)
        self.frozen_row_view.setFixedSize(vheader_width + viewport_width, row0_height)
        
        # Sync vertical header dimensions
        self.frozen_row_view.verticalHeader().setFixedWidth(vheader_width)
        self.frozen_row_view.verticalHeader().setDefaultSectionSize(row0_height)
        self.frozen_row_view.show()

    def on_row_resized(self, row, old_height, new_height):
        if row == 0:
            self.update_frozen_view_geometry()

    def update_frozen_column_width(self, logical_index, old_size, new_size):
        self.frozen_row_view.setColumnWidth(logical_index, new_size)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_row_count(self.verticalScrollBar().value())
        self.adjust_col_count(self.horizontalScrollBar().value())
        self.sync_frozen_column_widths()
        self.update_frozen_view_geometry()
    
    def adjust_row_count(self, value):
        if value == self.verticalScrollBar().maximum():
            self.controller.load_more_rows()
        else:
            last_row = self.rowAt(self.viewport().height() - 1)
            self.controller.load_less_rows(last_row)
    
    def adjust_col_count(self, value):
        if value == self.horizontalScrollBar().maximum():
            self.controller.load_more_cols()
        else:
            last_col = self.columnAt(self.viewport().width() - 1)
            self.controller.load_less_cols(last_col)