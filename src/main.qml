import QtQuick
import QtQuick.Controls
import QtQuick.Window

Window {
    width: 800
    height: 600
    visible: true
    title: "Auto-Resizing Spreadsheet"

    TableView {
        id: tableView
        anchors.fill: parent
        clip: true
        columnWidthProvider: function(column) { return spreadsheetModel.columnWidth(column) }
        rowHeightProvider: function(row) { return spreadsheetModel.rowHeight(row) }
        model: spreadsheetModel

        property Timer layoutTimer: Timer {
            interval: 0
            onTriggered: tableView.forceLayout()
        }

        delegate: Rectangle {
            id: cell
            implicitWidth: tableView.columnWidthProvider(column)
            implicitHeight: spreadsheetModel.rowHeight(row)
            border.color: "lightgray"

            property font cellFont: Qt.font({
                family: "Arial",
                pointSize: 12
            })

            required property int row
            required property int column
            required property string display

            property bool editing: false

            property Timer resizeTimer: Timer {
                interval: 50
                property int requiredWidth: 0
                onTriggered: {
                    spreadsheetModel.updateColumnWidth(column, requiredWidth)
                }
            }

            property Timer rowResizeTimer: Timer {
                interval: 50
                property int requiredHeight: 0
                onTriggered: {
                    spreadsheetModel.updateRowHeight(row, requiredHeight)
                }
            }

            Text {
                anchors.fill: parent
                text: cell.display
                verticalAlignment: Text.AlignVCenter
                leftPadding: 5
                visible: !cell.editing
                font: cell.cellFont
                wrapMode: Text.Wrap
            }

            TextEdit {
                id: editor
                anchors.fill: parent
                verticalAlignment: Text.AlignVCenter
                leftPadding: 5
                visible: cell.editing
                text: cell.display
                font: cell.cellFont
                wrapMode: Text.Wrap

                onActiveFocusChanged: if (!activeFocus) finishEditing()

                function finishEditing() {
                    cell.editing = false
                    spreadsheetModel.setCellData(row, column, editor.text)
                    editor.focus = false
                }

                Keys.onPressed: (event) => {
                    if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter) && !(event.modifiers & Qt.ShiftModifier)) {
                        finishEditing()
                        event.accepted = true
                    }
                }

                onTextChanged: {
                    textMetrics.text = text
                    const requiredWidth = textMetrics.width + 20
                    const currentWidth = tableView.columnWidthProvider(column)
                    if (requiredWidth > currentWidth) {
                        cell.resizeTimer.requiredWidth = requiredWidth
                        cell.resizeTimer.restart()
                    }

                    heightMetrics.text = text
                    heightMetrics.width = cell.implicitWidth
                    const requiredHeight = heightMetrics.implicitHeight + 10
                    if (requiredHeight > spreadsheetModel.rowHeight(row)) {
                        cell.rowResizeTimer.requiredHeight = requiredHeight
                        cell.rowResizeTimer.restart()
                    }
                }
            }

            TextMetrics {
                id: textMetrics
                font: cell.cellFont
            }

            Text {
                id: heightMetrics
                text: editor.text
                width: cell.implicitWidth
                font: cell.cellFont
                wrapMode: Text.Wrap
                elide: Text.ElideNone
                visible: false
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    cell.editing = true
                    editor.forceActiveFocus()
                }
            }

            onImplicitWidthChanged: {
                heightMetrics.text = editor.text
                heightMetrics.width = implicitWidth
                const requiredHeight = heightMetrics.implicitHeight + 10
                if (requiredHeight > spreadsheetModel.rowHeight(row)) {
                    cell.rowResizeTimer.requiredHeight = requiredHeight
                    cell.rowResizeTimer.restart()
                }
            }
        }

        Connections {
            target: spreadsheetModel
            function onColumn_width_changed(column) {
                tableView.layoutTimer.restart()
            }
            function onRow_height_changed(row) {
                tableView.layoutTimer.restart()
            }
        }
    }
}