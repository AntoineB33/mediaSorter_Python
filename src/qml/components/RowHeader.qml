import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ListView {
    id: rowHeader
    Layout.preferredWidth: 40
    Layout.fillHeight: true  // Add this line
    model: spreadsheetModel.rowCount()
    boundsBehavior: Flickable.StopAtBounds
    interactive: false
    clip: true

    delegate: Rectangle {
        width: rowHeader.width
        height: tableView.cellHeight
        color: "#f0f0f0"
        border.color: "#cccccc"
        
        Text {
            text: index + 1
            anchors.centerIn: parent
            font.pixelSize: 12
        }
    }

    contentY: tableView.contentY

    Connections {
        target: spreadsheetModel
        function onRowsInserted(parent, first, last) { 
            rowHeader.model = spreadsheetModel.rowCount(); 
        }
        function onRowsRemoved(parent, first, last) { 
            rowHeader.model = spreadsheetModel.rowCount(); 
        }
    }
}