import QtQuick

Rectangle {
    id: cell
    implicitWidth: spreadsheetModel.columnWidth(column)
    implicitHeight: spreadsheetModel.rowHeight(row)
    color: spreadsheetModel.get_cell_color(row, column)
    border.color: "lightgray"
    border.width: 1

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

    property int selectedRow: -1
    property int selectedColumn: -1

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
            cell.border.color = "lightgray"
            cell.border.width = 1
        }

        Keys.onPressed: (event) => {
            if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter) && !(event.modifiers & Qt.ShiftModifier)) {
                finishEditing()
                event.accepted = true
            }
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
            cell.border.color = "black"
            cell.border.width = 3
            cell.selectedRow = row
            cell.selectedColumn = column
            editor.forceActiveFocus()
            floatingWindow.currentColumn = column
        }
    }
    
    // Add connection to handle background updates
    Connections {
        target: spreadsheetModel
        function onDataChanged(topLeft, bottomRight, roles) {
            if (topLeft.row <= 0 && bottomRight.row >= 0 && 
                topLeft.column <= column && bottomRight.column >= column) {
                // Update the display property
                if (row == 0) {
                    cellDelegate.display = spreadsheetModel.data(
                        spreadsheetModel.index(row, column), 
                        Qt.DisplayRole
                    )
                }
                // Update background if BackgroundRole changed
                if (roles.includes(Qt.BackgroundRole)) {
                    color = spreadsheetModel.get_cell_color(row, column)
                }
            }
        }
    }
}