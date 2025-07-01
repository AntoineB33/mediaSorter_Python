import QtQuick

Rectangle {
    id: cell
    implicitWidth: spreadsheetModel.columnWidth(column)
    implicitHeight: spreadsheetModel.rowHeight(row)
    color: background
    border.color: decoration === 2 ? "black" : 
                  decoration === 1 ? "gray" : "lightgray"
    border.width: decoration + 1

    property int verticalPadding: spreadsheetModel.get_vertical_padding()
    property font cellFont: Qt.font({
        family: spreadsheetModel.get_font_family(),
        pointSize: spreadsheetModel.get_font_size(),
    })
    
    required property int index
    required property int column
    required property int row
    property bool editing: false
    property string editText: ""  // Added to track edited text
    // property var display: spreadsheetModel.data(spreadsheetModel.index(0, index), Qt.DisplayRole)
    // property var background: spreadsheetModel.data(spreadsheetModel.index(0, index), Qt.BackgroundRole)
    // property var decoration: spreadsheetModel.data(spreadsheetModel.index(0, index), Qt.DecorationRole)
    required property var display    // For DisplayRole
    required property var background // For BackgroundRole
    required property var decoration // For DecorationRole


    Text {
        anchors.fill: parent
        text: cell.display
        verticalAlignment: Text.AlignVCenter
        leftPadding: cell.verticalPadding
        rightPadding: cell.verticalPadding
        visible: !cell.editing
        font: cell.cellFont
        Keys.onPressed: (event) => {
            check_for_pasting(event)
        }
    }

    function check_for_pasting(event) {
        if (event.key === Qt.Key_V && (event.modifiers & Qt.ControlModifier)) {
            event.accepted = true
            Qt.callLater(function() {
                var clipboardText = ClipboardHelper.getText()
                if (clipboardText) {
                    // Parse clipboard data
                    var rows = clipboardText.split(/\r\n|\n|\r/)
                    var data = []
                    for (var i = 0; i < rows.length; i++) {
                        if (rows[i]) { // Skip empty lines
                            data.push(rows[i].split('\t'))
                        }
                    }
                    console.log("Pasting data:", data)
                    
                    // Handle single cell paste
                    if (data.length === 1 && data[0].length === 1) {
                        editor.insert(editor.cursorPosition, data[0][0])
                    } 
                    // Handle multi-cell paste
                    else if (data.length > 0) {
                        editor.finishEditing()
                        spreadsheetModel.setBlockData(row, column, data)
                    }
                }
            })
        }
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
            check_for_pasting(event)
        }
        
        onTextChanged: {
            // Only update the model if the text is different from the display value
            if (text !== cell.display) {
                var modelIndex = spreadsheetModel.index(row, column)
                var success = spreadsheetModel.setData(modelIndex, text, Qt.EditRole)
            }
        }

        // Removed onTextChanged that updated the model
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            cell.forceActiveFocus()
            cell.editing = true
            cell.editText = cell.display
            spreadsheetModel.cellClicked(row, column)
            editor.forceActiveFocus()
        }
    }
}