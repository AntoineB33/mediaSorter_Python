import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Window {
    id: mainWindow
    width: 800
    height: 600
    visible: true
    title: "Dynamic Spreadsheet"

    // Remove spreadsheetModel property declaration

    RowLayout {
        anchors.fill: parent
        spacing: 0

        ListView {
            id: rowHeader
            model: spreadsheetModel.rowCount()
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
                function onRowsInserted(parent, first, last) { rowHeader.model = spreadsheetModel.rowCount() }
                function onRowsRemoved(parent, first, last) { rowHeader.model = spreadsheetModel.rowCount() }
            }
        }

        SpreadsheetTableView {
            id: tableView
            spreadsheetModel: spreadsheetModel // Access context property directly

            Component.onCompleted: {
                const initRows = Math.max(spreadsheetModel.getMaxRow(), Math.floor(height / cellHeight + 1))
                const initCols = Math.max(spreadsheetModel.getMaxColumn(), Math.floor(width / cellWidth + 1))
                spreadsheetModel.setRows(initRows)
                spreadsheetModel.setColumns(initCols)
            }
        }
    }

    FloatingWindow {
        spreadsheetModel: spreadsheetModel // Access context property directly
    }
}