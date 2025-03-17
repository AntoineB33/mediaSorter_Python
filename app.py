import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from models.infinite_table_model import InfiniteTableModel
from controllers.main_controller import MainController

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    
    # Initialize components
    engine = QQmlApplicationEngine()
    controller = MainController()
    model = InfiniteTableModel(controller, "collection")
    
    # Expose to QML
    engine.rootContext().setContextProperty("infiniteModel", model)
    engine.rootContext().setContextProperty("controller", controller)
    
    # Load QML
    engine.load("qml/main.qml")
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec())