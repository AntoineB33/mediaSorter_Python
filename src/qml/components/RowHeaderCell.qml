import QtQuick

Rectangle {
    id: root
    property int rowIndex: 1

    width: 40 // or parent.width
    height: 30 // or some default
    color: "#f0f0f0"
    border.color: "#cccccc"

    Text {
        anchors.centerIn: parent
        text: rowIndex
        font.pixelSize: 12
    }
}
