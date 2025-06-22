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
        // function onDataChanged(topLeft, bottomRight, roles) {
        //     if (topLeft.column === 0) {
        //         // Force model update when first row changes
        //         rowHeader.model = 0
        //         rowHeader.model = spreadsheetModel.rowCount();
        //     }
        // }
        // function onDataChanged(topLeft, bottomRight, roles) {
        //     if (topLeft.column == 0) {
        //         const startRow = topLeft.row
        //         const endRow = bottomRight.row

        //         for (let row = startRow; row <= endRow; row++) {
        //             const item = rowHeader.itemAt(row)
        //             if (item) {
        //                 item.decorationChanged()
        //             }
        //         }
        //     }
        // }
    }
}