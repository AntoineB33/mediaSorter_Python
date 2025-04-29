import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: mainLayout
    property alias tableView: tableView
    anchors.fill: parent
    spacing: 0

    property int cellHeight : spreadsheetModel.getCellHeight()

    // Hidden Text element to measure the widest row index
    Text {
        id: textMeasurer
        visible: false
        Component.onCompleted: {
            spreadsheetModel.setTextMeasurer(textMeasurer)
        }
    }

    ColumnLayout {
        id: colLayout

        Text {
            id: indexMeasurer
            visible: false
            text: spreadsheetModel.count
        }

        property int rowHeaderWidth: indexMeasurer.width + spreadsheetModel.cellHorizPaddings

        RowHeaderCell {
            id: topLeft
            width: colLayout.rowHeaderWidth
            height: cellHeight
            rowIndex: 1
        }

        RowHeader {
            id: rowHeader
            width: colLayout.rowHeaderWidth
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