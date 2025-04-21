import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: mainLayout
    property alias tableView: tableView
    anchors.fill: parent
    spacing: 0

    RowHeader {
        Layout.preferredWidth: 40
        Layout.fillHeight: true
        cellHeight: tableView.cellHeight
    }

    SpreadsheetTableView {
        id: tableView
        Layout.fillWidth: true
        Layout.fillHeight: true
    }
}