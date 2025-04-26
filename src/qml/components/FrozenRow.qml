import QtQuick
import QtQuick.Controls

Rectangle {
    id: frozenRow
    width: rowHeader.width
    height: tableView.cellHeight
    color: "#e0e0e0"
    border.color: "#aaaaaa"

    Text {
        text: "1"
        anchors.centerIn: parent
        font.pixelSize: 12
    }

    // Optional: bind to data if necessary
}
