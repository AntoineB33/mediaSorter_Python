import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ListView {
    id: frozenFirstRow
    orientation: Qt.Horizontal
    Layout.preferredHeight: spreadsheetModel.rowHeight(0)
    Layout.fillWidth: true
    boundsBehavior: Flickable.StopAtBounds
    interactive: false
    clip: true
    model: headerModel

    delegate: CellDelegate {
        width: headerModel.columnWidth(index)
        height: headerModel.rowHeight(0)
        text: model.display
        header: true
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