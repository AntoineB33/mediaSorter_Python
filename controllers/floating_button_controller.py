class FloatingButtonController:
    """
    Controller for handling color changes in the table.
    """
    def __init__(self, model):
        self.model = model  # Reference to the model

    def change_column_color(self, column, color):
        """Handles color change request for a given column."""
        if column is not None:
            self.model.set_column_color(column, color)