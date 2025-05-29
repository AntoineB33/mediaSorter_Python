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
        id: cellDelegate
        row: 0
        column: index
        display: spreadsheetModel.data(spreadsheetModel.index(0, index), Qt.DisplayRole)
        // Add a connection to listen for data changes
        Connections {
            target: spreadsheetModel
            function onDataChanged(topLeft, bottomRight, roles) {
                // Check if this cell's data was changed
                if (topLeft.row <= 0 && bottomRight.row >= 0 && 
                    topLeft.column <= index && bottomRight.column >= index) {
                    // Update the display property
                    cellDelegate.display = spreadsheetModel.data(
                        spreadsheetModel.index(0, index), 
                        Qt.DisplayRole
                    )
                }
            }
        }
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