import random

class RoleTypes:
    NAMES = "names"
    DEPENDENCIES = "dependencies"
    ATTRIBUTES_TO_SPRAWL = "attributes_to_sprawl"
    ATTRIBUTES = "attributes"
    POINTERS = "pointers"
    PATH = "path"

class collectionElement:
    def __init__(self, rowHeights, columnWidths):
        self.data = [["names"]]
        self.roles = ["names"]
        self.rowHeights = rowHeights
        self.columnWidths = columnWidths

class collection:
    def __init__(self):
        self.collections = {}
        self.checkings_list = []
        self.sortings_list = []
        self.collectionName = ""