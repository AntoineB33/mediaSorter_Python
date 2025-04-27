import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: mainLayout
    property alias tableView: tableView
    anchors.fill: parent
    spacing: 0

    property int cellHeight : spreadsheetModel.getCellHeight()

    FrozenRow {
        id: frozenRow
        width: rowHeaderWidth
        height: cellHeight
        Layout.fillWidth: true
        color: "lightgray"
        Text {
            anchors.centerIn: parent
            text: "1"
        }
    }

    // Hidden Text element to measure the widest row index
    Text {
        id: textMeasurer
        visible: false
        font: Qt.font({ pointSize: 10 }) // Match the font used in row header delegate
        text: spreadsheetModel.rowCount().toString() // Get the last row index (e.g., "100")
    }

    // Compute row header width based on the widest text, with padding
    property int rowHeaderWidth: textMeasurer.width + spreadsheetModel.getCellHorizPaddings()

    RowHeaderCell {
        id: topLeft
        width: rowHeaderWidth
        height: cellHeight
        rowIndex: 1
    }

    RowHeader {
        id: rowHeader
        width: rowHeaderWidth
        Layout.fillHeight: true
    }

    SpreadsheetTableView {
        id: tableView
        Layout.fillWidth: true
        Layout.fillHeight: true
    }
}