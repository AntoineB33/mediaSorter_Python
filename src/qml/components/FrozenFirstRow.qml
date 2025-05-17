import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ListView {
    id: frozenFirstRow
    orientation: Qt.Horizontal
    Layout.preferredHeight: spreadsheetModel.rowHeight(0)
    Layout.fillWidth: true
    model: spreadsheetModel.columnCount()
    boundsBehavior: Flickable.StopAtBounds
    interactive: false
    clip: true

    delegate: CellDelegate {
        row: 0
        column: index
        display: spreadsheetModel.data(spreadsheetModel.index(0, index), Qt.DisplayRole)
    }

    contentX: tableView.contentX

    Connections {
        target: spreadsheetModel
        function onColumnsInserted(parent, first, last) {
            frozenFirstRow.model = spreadsheetModel.columnCount();
        }
        function onColumnsRemoved(parent, first, last) { 
            frozenFirstRow.model = spreadsheetModel.columnCount(); 
        }
    }
}