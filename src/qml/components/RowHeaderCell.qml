import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    width: 40
    height: spreadsheetModel.rowHeight(index)
    color: "#f0f0f0"
    border.color: "#cccccc"
    // border.width: decoration + 1

    property int index: 0
    property var decoration: spreadsheetModel.data(spreadsheetModel.index(index, 0), Qt.DecorationRole)
    
    Text {
        text: index + 1
        anchors.centerIn: parent
        font.pixelSize: 12
    }

    // Connections {
    //     target: spreadsheetModel
    //     function onDataChanged(topLeft, bottomRight, roles) {
    //         if (topLeft.column === 0) {
    //             // Force model update when first row changes
    //             rowHeader.model = 0
    //             rowHeader.model = spreadsheetModel.rowCount();
    //         }
    //     }
    // }
}