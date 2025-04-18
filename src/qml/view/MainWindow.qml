// view/MainWindow.qml
import QtQuick
import QtQuick.Controls

Window {
    id: mainWindow
    // Window properties and basic layout
    RowLayout {
        anchors.fill: parent
        spacing: 0
        
        RowHeader {}
        SpreadsheetTableView {}
    }
    
    FloatingWindow {
        // Positioning logic
    }
}