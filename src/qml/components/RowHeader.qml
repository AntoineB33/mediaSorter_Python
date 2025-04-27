import QtQuick
import QtQuick.Controls

ListView {
    id: rowHeader
    model: spreadsheetModel.rowCount() - 1
    boundsBehavior: Flickable.StopAtBounds
    interactive: false
    clip: true

    delegate: RowHeaderCell {
        width: rowHeader.width
        height: spreadsheetModel.rowHeight(index + 1)
        rowIndex: index + 2
    }

    contentY: tableView.contentY

    Connections {
        target: spreadsheetModel
        function onRowsInserted(parent, first, last) { 
            rowHeader.model = spreadsheetModel.rowCount() - 1; 
        }
        function onRowsRemoved(parent, first, last) { 
            rowHeader.model = spreadsheetModel.rowCount() - 1; 
        }
    }
}