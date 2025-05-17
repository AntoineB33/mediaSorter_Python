import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    width: 40
    height: spreadsheetModel.rowHeight(index)
    color: "#f0f0f0"
    border.color: "#cccccc"

    property int index: 0
    
    Text {
        text: index + 1
        anchors.centerIn: parent
        font.pixelSize: 12
    }
}