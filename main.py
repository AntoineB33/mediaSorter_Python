import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    engine = QQmlApplicationEngine()
    engine.load("main.qml")
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec())