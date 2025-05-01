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
        model: spreadsheetModel

        property Timer layoutTimer: Timer {
            interval: 0
            onTriggered: tableView.forceLayout()
        }

        delegate: Rectangle {
            id: cell
            implicitWidth: tableView.columnWidthProvider(column)
            implicitHeight: 30
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

            Text {
                anchors.fill: parent
                text: cell.display
                verticalAlignment: Text.AlignVCenter
                leftPadding: 5
                visible: !cell.editing
                font: cell.cellFont
            }

            TextInput {
                id: editor
                anchors.fill: parent
                verticalAlignment: Text.AlignVCenter
                leftPadding: 5
                visible: cell.editing
                text: cell.display
                font: cell.cellFont

                onActiveFocusChanged: if (!activeFocus) finishEditing()
                onEditingFinished: finishEditing()

                function finishEditing() {
                    cell.editing = false
                    spreadsheetModel.setCellData(row, column, editor.text)
                    editor.focus = false  // Add this line to ensure focus release
                }

                onTextChanged: {
                    textMetrics.text = text
                    const requiredWidth = textMetrics.width + 20
                    const currentWidth = tableView.columnWidthProvider(column)
                    if (requiredWidth > currentWidth) {
                        cell.resizeTimer.requiredWidth = requiredWidth
                        cell.resizeTimer.restart()
                    }
                }
            }

            TextMetrics {
                id: textMetrics
                font: cell.cellFont
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    cell.editing = true
                    editor.forceActiveFocus()
                }
            }
        }

        Connections {
            target: spreadsheetModel
            function onColumn_width_changed(column) {
                tableView.layoutTimer.restart()
            }
        }
    }
}