import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: mainLayout
    property alias tableView: tableView
    anchors.fill: parent
    spacing: 0

    ColumnLayout {
        spacing: 0

        RowHeaderCell {}
        RowHeader {}
    }

    ColumnLayout {
        spacing: 0

        FrozenFirstRow {}
        SpreadsheetTableView {
            id: tableView
        }
    }
}