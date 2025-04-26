import QtQuick
import QtQuick.Controls

ListView {
    id: rowHeader
    model: spreadsheetModel.rowCount() - 1
    boundsBehavior: Flickable.StopAtBounds
    interactive: false
    clip: true

    delegate: Rectangle {
        width: rowHeader.width
        height: tableView.cellHeight
        color: "#f0f0f0"
        border.color: "#cccccc"
        
        Text {
            text: index + 2
            anchors.centerIn: parent
            font.pixelSize: 12
        }
    }

    contentY: tableView.contentY

    Connections {
        target: spreadsheetModel
        function onRowsInserted(parent, first, last) { 
            rowHeader.model = spreadsheetModel.rowCount() - 1; 
        }
        function onRowsRemoved(parent, first, last) { 
            rowHeader.model = spreadsheetModel.rowCount() - 1; 
        }
    }
}