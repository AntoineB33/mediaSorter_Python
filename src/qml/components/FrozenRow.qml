import QtQuick
import QtQuick.Controls

ListView {
    id: frozenRow
    model: spreadsheetModel.columnCount() - 1
    boundsBehavior: Flickable.StopAtBounds
    // interactive: false
    clip: true

    delegate: CellDelegate {}

    contentX: tableView.contentX

    Connections {
        target: spreadsheetModel
        function onColumnsInserted(parent, first, last) { 
            frozenRow.model = spreadsheetModel.columnCount() - 1; 
        }
        function onColumnsRemoved(parent, first, last) {
            frozenRow.model = spreadsheetModel.columnCount() - 1; 
        }
    }
}