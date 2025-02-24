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
        self.last_viewport_size = None

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

    def delayed_resize_adjustment(self):
        """Handle resize completion after window animation finishes"""
        current_size = self.viewport().size()
        
        # Compare width AND height
        if (self.last_viewport_size and 
            (self.last_viewport_size.width() != current_size.width() or
            self.last_viewport_size.height() != current_size.height())):
            self.last_viewport_size = current_size
            self.adjust_to_viewport()
            self.sync_frozen_column_widths()
            self.update_frozen_view_geometry()
        elif not self.last_viewport_size:  # Initial case
            self.adjust_to_viewport()
            self.update_frozen_view_geometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Use single-shot timer to ensure this runs after resize completes
        QTimer.singleShot(50, self.delayed_resize_adjustment)

    def adjust_to_viewport(self):
        """Ensure enough rows/columns to fill current viewport"""
        self.adjust_row_count_immediate()
        self.adjust_col_count_immediate()

    def adjust_row_count_immediate(self):
        """Force row check without waiting for scroll"""
        scrollbar = self.verticalScrollBar()
        max_pos = scrollbar.maximum()
        current_pos = scrollbar.value()
        
        # Check both top and bottom boundaries
        if current_pos == max_pos:
            self.controller.load_more_rows()
        elif current_pos == scrollbar.minimum():
            self.controller.load_less_rows(0)
        else:
            # Calculate how many rows fit in viewport
            viewport_height = self.viewport().height()
            if self.model().rowCount() == 0:
                return
            row_height = self.rowHeight(0)
            if row_height == 0: row_height = 25  # Default height
            visible_rows = viewport_height // row_height
            if self.model().rowCount() < visible_rows:
                self.controller.load_more_rows()

    def adjust_col_count_immediate(self):
        """Force column check without waiting for scroll"""
        scrollbar = self.horizontalScrollBar()
        max_pos = scrollbar.maximum()
        current_pos = scrollbar.value()
        
        if current_pos == max_pos:
            self.controller.load_more_cols()
        elif current_pos == scrollbar.minimum():
            self.controller.load_less_cols(0)
        else:
            # Calculate how many columns fit in viewport
            viewport_width = self.viewport().width()
            first_col_width = self.columnWidth(0) if self.model().columnCount() > 0 else 100  # Default width
            if first_col_width == 0: first_col_width = 100  # Prevent division by zero
            visible_cols = viewport_width // first_col_width
            if self.model().columnCount() < visible_cols:
                self.controller.load_more_cols()



    def changeEvent(self, event):
        """Handle window state changes"""
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            # Handle both maximize and restore events
            self.delayed_resize_adjustment()

    
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