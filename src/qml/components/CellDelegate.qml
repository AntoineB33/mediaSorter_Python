import QtQuick

Rectangle {
    id: cell
    implicitWidth: spreadsheetModel.columnWidth(column)
    implicitHeight: spreadsheetModel.rowHeight(row)
    border.color: "lightgray"

    property int verticalPadding: spreadsheetModel.get_vertical_padding()
    property font cellFont: Qt.font({
        family: spreadsheetModel.get_font_family(),
        pointSize: spreadsheetModel.get_font_size(),
    })
    
    required property int index
    required property int column
    required property int row
    required property string display
    property bool editing: false
    property string editText: ""  // Added to track edited text

    Text {
        anchors.fill: parent
        text: cell.display
        verticalAlignment: Text.AlignVCenter
        leftPadding: cell.verticalPadding
        rightPadding: cell.verticalPadding
        visible: !cell.editing
        font: cell.cellFont
    }

    TextEdit {
        id: editor
        anchors.fill: parent
        verticalAlignment: Text.AlignVCenter
        leftPadding: cell.verticalPadding
        rightPadding: cell.verticalPadding
        visible: cell.editing
        text: cell.editText  // Bind to editText instead of display
        font: cell.cellFont

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
            // Update model immediately on text change
            var modelIndex = spreadsheetModel.index(row, column)
            var success = spreadsheetModel.setData(modelIndex, text, Qt.EditRole)
        }

        // Removed onTextChanged that updated the model
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            cell.editing = true
            cell.editText = cell.display  // Initialize editText with current value
            editor.forceActiveFocus()
        }
    }
}