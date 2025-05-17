import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ListView {
    id: rowHeader
    Layout.preferredWidth: 40
    Layout.fillHeight: true  // Add this line
    model: spreadsheetModel.rowCount()
    boundsBehavior: Flickable.StopAtBounds
    interactive: false
    clip: true

    delegate: RowHeaderCell {
        id: rowHeaderCell
        index: model.index + 1
    }

    contentY: tableView.contentY

    Connections {
        target: spreadsheetModel
        function onRowsInserted(parent, first, last) {
            rowHeader.model = spreadsheetModel.rowCount();
        }
        function onRowsRemoved(parent, first, last) { 
            rowHeader.model = spreadsheetModel.rowCount(); 
        }
    }
}