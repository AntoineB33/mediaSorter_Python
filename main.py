import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

if __name__ == "__main__":
    # Create the Qt application
    app = QGuiApplication(sys.argv)
    
    # Create the QML engine
    engine = QQmlApplicationEngine()
    
    # Set the list of all possible suggestions as a context property
    suggestions = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"]
    engine.rootContext().setContextProperty("allSuggestions", suggestions)
    
    # Load the QML file
    engine.load("main.qml")
    
    # Check if the QML file loaded successfully
    if not engine.rootObjects():
        sys.exit(-1)
    
    # Run the application
    sys.exit(app.exec())