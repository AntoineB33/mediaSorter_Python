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
        background: spreadsheetModel.data(spreadsheetModel.index(0, index), Qt.BackgroundRole)
        decoration: spreadsheetModel.data(spreadsheetModel.index(0, index), Qt.DecorationRole)
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
        function onDataChanged(topLeft, bottomRight, roles) {
            if (topLeft.row === 0 || bottomRight.row === 0) {
                // Force model update when first row changes
                frozenFirstRow.model = 0
                frozenFirstRow.model = spreadsheetModel.columnCount()
            }
        }
        // function onDataChanged2(topLeft, bottomRight, roles) {
        //     // Only update if change affects first row
        //     if (topLeft.row <= 0 && bottomRight.row >= 0) {
        //         // Let QML's built-in update mechanism handle the changes
        //         // This is similar to how TableView works internally
        //         const startCol = topLeft.column
        //         const endCol = bottomRight.column
                
        //         // This triggers QML to update the affected items
        //         for (let col = startCol; col <= endCol; col++) {
        //             const item = frozenFirstRow.itemAt(col)
        //             if (item) {
        //                 // We don't need to update properties manually here
        //                 // The bindings will automatically refresh
        //                 item.displayChanged()
        //                 item.backgroundChanged()
        //                 item.decorationChanged()
        //             }
        //         }
        //     }
        // }
    }
}