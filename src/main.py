import sys
import json
import os
from pathlib import Path
from PySide6.QtCore import QAbstractTableModel, Qt, QUrl, QModelIndex, Slot, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from models.spreadsheet_model import SpreadsheetModel
from qasync import QEventLoop, asyncSlot
import asyncio


async def main():
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

    app = QGuiApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    engine = QQmlApplicationEngine()
    current_dir = Path(__file__).parent
    qml_dir = current_dir / "qml"
    engine.addImportPath(str(qml_dir))
    
    # Create model BEFORE loading QML
    model = SpreadsheetModel()
    engine.rootContext().setContextProperty("spreadsheetModel", model)
    
    qml_file = qml_dir / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    model.start_background_tasks()

    with loop:
        sys.exit(loop.run_forever())


if __name__ == "__main__":
    asyncio.run(main())