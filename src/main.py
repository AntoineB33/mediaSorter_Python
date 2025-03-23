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
    
    # 1. Set context property FIRST
    engine.rootContext().setContextProperty("spreadsheetModel", model)
    
    # 2. Configure paths AFTER setting context
    current_dir = Path(__file__).parent
    qml_dir = current_dir / "qml"
    engine.addImportPath(str(qml_dir))
    
    # 3. Load QML LAST
    qml_file = qml_dir / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    # Clean exit if load fails
    if not engine.rootObjects():
        sys.exit(-1)
    
    # Connect save handler
    app.aboutToQuit.connect(model.save_to_file)
    
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()