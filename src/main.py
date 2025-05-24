import sys
import json
import os
from pathlib import Path
from PySide6.QtCore import QAbstractTableModel, Qt, QUrl, QModelIndex, Slot, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from models.spreadsheet_model import HeaderProxyModel, DataProxyModel, SpreadsheetModel

def main():
    # Set the QT_QUICK_CONTROLS_STYLE environment variable
    # os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"  # Set the style to Fusion

    app = QGuiApplication(sys.argv)
    spreadsheetModel = SpreadsheetModel()
    header_model = HeaderProxyModel()
    header_model.setSourceModel(spreadsheetModel)
    data_model = DataProxyModel()
    data_model.setSourceModel(spreadsheetModel)
    
    engine = QQmlApplicationEngine()

    # 1. Set context property FIRST
    engine.rootContext().setContextProperty("headerModel", header_model)
    engine.rootContext().setContextProperty("dataModel", data_model)
    engine.rootContext().setContextProperty("spreadsheetModel", spreadsheetModel)
    
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
    app.aboutToQuit.connect(spreadsheetModel.save_to_file)
    
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()