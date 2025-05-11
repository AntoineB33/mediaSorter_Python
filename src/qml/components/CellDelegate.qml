import QtQuick

Rectangle {
    id: cell
    implicitWidth: spreadsheetModel.columnWidth(column)
    implicitHeight: spreadsheetModel.rowHeight(row)
    border.color: "lightgray"

    property font cellFont: Qt.font({
        family: "Arial",
        pointSize: 12
    })

    required property int column
    required property int row
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
            editor.focus = false
        }

        Keys.onPressed: (event) => {
            if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter) && !(event.modifiers & Qt.ShiftModifier)) {
                finishEditing()
                event.accepted = true
            }
        }

        onTextChanged: {
            // Update the model with the new text
            var modelIndex = spreadsheetModel.index(row, column)
            console.log("Updating model at row:", row, "column:", column, "with text:", text)
            var success = spreadsheetModel.setData(modelIndex, text, Qt.EditRole)

            textMetrics.text = text
            const requiredWidth = textMetrics.width + 20
            const currentWidth = spreadsheetModel.columnWidth(column)
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