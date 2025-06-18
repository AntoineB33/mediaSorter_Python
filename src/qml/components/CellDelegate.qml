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
            floatingWindow.currentColumn = column
        }
    }
    
    // Add connection to handle background updates
    Connections {
        target: spreadsheetModel
        function onDataChanged(topLeft, bottomRight, roles) {
            if (topLeft.row <= row && row <= bottomRight.row && 
                topLeft.column <= column && column <= bottomRight.column) {
                if (row == 0) {
                    cellDelegate.display = spreadsheetModel.data(
                        spreadsheetModel.index(row, column), 
                        Qt.DisplayRole
                    )
                }
                if (roles.includes(Qt.BackgroundRole)) {
                    color = spreadsheetModel.get_cell_color(row, column)
                }
                if (roles.includes(Qt.DecorationRole)) {
                    var decoration = spreadsheetModel.data(
                        spreadsheetModel.index(row, column), 
                        Qt.DecorationRole
                    );
                    if (decoration == 2) {
                        console.log("Decoration 2 for cell at", row, column);
                    }
                    cell.border.color = decoration == 0 ? "lightgray" : 
                        decoration == 2 ? "black" : "lightgreen";
                    cell.border.width = decoration == 2 ? 3 : 1;
                }
            }
        }
    }
}