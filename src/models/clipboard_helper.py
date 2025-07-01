# clipboard_helper.py
from PySide6.QtCore import QObject, Slot, Property
from PySide6.QtGui import QGuiApplication

class ClipboardHelper(QObject):
    @Slot(result=str)
    def getText(self):
        return QGuiApplication.clipboard().text()

    @Slot(str)
    def setText(self, text):
        QGuiApplication.clipboard().setText(text)
