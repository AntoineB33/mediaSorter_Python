import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl, QObject, Signal, Slot, Property, Qt
from PySide2.QtGui import QGuiApplication

class SuggestionsHandler(QObject):
    def __init__(self):
        super().__init__()
        self._suggestions = []
        self.all_items = [
            "Apple", "Banana", "Cherry", "Date", "Elderberry",
            "Fig", "Grape", "Honeydew", "Kiwi", "Lemon"
        ]

    # Signal to send suggestions to QML
    suggestionsChanged = Signal(list)

    @Property(list, notify=suggestionsChanged)
    def suggestions(self):
        return self._suggestions

    @Slot(str)
    def update_suggestions(self, text):
        if text:
            self._suggestions = [item for item in self.all_items if text.lower() in item.lower()]
        else:
            self._suggestions = []
        self.suggestionsChanged.emit(self._suggestions)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    handler = SuggestionsHandler()
    
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    context = view.rootContext()
    context.setContextProperty("suggestionHandler", handler)
    
    view.setSource(QUrl.fromLocalFile('main.qml'))
    
    if view.status() == QQuickView.Error:
        sys.exit(-1)
    
    view.show()
    sys.exit(app.exec_())