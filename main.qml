// main.qml (updated view component)
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    width: 800
    height: 600
    visible: true
    title: "Smooth Scroll Spreadsheet"

    TableView {
        id: tableView
        anchors.fill: parent
        model: spreadsheetModel
        clip: true

        property real cellWidth: 100
        property real cellHeight: 30
        property real minExtraSpace: 20  // Minimum extra space to ensure scrollability

        Component.onCompleted: {
            // Initial rows/columns with buffer space for scrolling
            const initRows = Math.ceil(height / cellHeight) + 1
            const initCols = Math.ceil(width / cellWidth) + 1
            spreadsheetModel.addRows(initRows)
            spreadsheetModel.addColumns(initCols)
        }

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AlwaysOn
            onPositionChanged: {
                // Calculate remaining space below visible area
                const contentBottom = tableView.contentY + tableView.height
                const totalHeight = spreadsheetModel.rowCount * tableView.cellHeight
                const remainingSpace = totalHeight - contentBottom
                
                // Add row when within 1 cell height of bottom
                if (remainingSpace <= tableView.cellHeight) {
                    spreadsheetModel.addRows(1)
                }
            }
        }

        ScrollBar.horizontal: ScrollBar {
            policy: ScrollBar.AlwaysOn
            onPositionChanged: {
                // Calculate remaining space to the right
                const contentRight = tableView.contentX + tableView.width
                const totalWidth = spreadsheetModel.columnCount * tableView.cellWidth
                const remainingSpace = totalWidth - contentRight
                
                // Add column when within 1 cell width of right
                if (remainingSpace <= tableView.cellWidth) {
                    spreadsheetModel.addColumns(1)
                }
            }
        }

        delegate: Rectangle {
            implicitWidth: tableView.cellWidth
            implicitHeight: tableView.cellHeight
            border.color: "lightgray"

            TextInput {
                anchors.fill: parent
                anchors.margins: 2
                text: model.display
                onEditingFinished: model.display = text
            }
        }
    }
}