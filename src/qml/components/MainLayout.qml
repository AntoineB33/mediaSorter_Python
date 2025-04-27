import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: mainLayout
    property alias tableView: tableView
    anchors.fill: parent
    spacing: 0

    property int cellHeight : spreadsheetModel.getCellHeight()

    ColumnLayout {
        // Hidden Text element to measure the widest row index
        Text {
            id: textMeasurer
            visible: false
            font: spreadsheetModel.get.font()
            text: spreadsheetModel.rowCount().toString()
        }
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
    }

    ColumnLayout {
        FrozenRow {
            id: frozenRow
            Layout.fillWidth: true
            height: cellHeight
        }

        SpreadsheetTableView {
            id: tableView
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}