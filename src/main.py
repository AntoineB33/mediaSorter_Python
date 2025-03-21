import sys
import json
import os
from pathlib import Path
from PySide6.QtCore import QAbstractTableModel, Qt, QUrl, QModelIndex, Slot, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from models.spreadsheet_model import SpreadsheetModel

def main():
    app = QGuiApplication(sys.argv)
    model = SpreadsheetModel()
    
    engine = QQmlApplicationEngine()
    
    # Get the absolute path to the QML directory
    current_dir = Path(__file__).parent
    qml_dir = current_dir / "qml"
    
    # Set import paths and load main QML
    engine.addImportPath(str(qml_dir))
    
    # Load main QML file with full path
    qml_file = qml_dir / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    # Save data when app quits
    app.aboutToQuit.connect(model.save_to_file)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()