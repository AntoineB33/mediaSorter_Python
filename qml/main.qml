import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    width: 1024
    height: 768
    visible: true

    SpreadsheetGrid {
        anchors.fill: parent
        model: tableModel  // Exposed from Python
    }
}