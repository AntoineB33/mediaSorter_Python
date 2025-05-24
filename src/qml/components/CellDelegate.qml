import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    property alias text: textInput.text
    property bool header: false
    property bool editing: false
    
    implicitWidth: 100
    implicitHeight: 40
    
    color: header ? "#f0f0f0" : "#ffffff"
    border.color: editing ? "blue" : "#d0d0d0"

    Text {
        id: displayText
        anchors.fill: parent
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        text: parent.text
        visible: !editing
        font.bold: header
        color: header ? "#404040" : "#000000"
    }

    TextInput {
        id: textInput
        anchors.fill: parent
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        visible: editing
        font: displayText.font
        selectByMouse: true
        onAccepted: {
            // Commit changes when pressing Enter
            if (editing) {
                editing = false
                spreadsheetModel.setData(spreadsheetModel.index, text, Qt.EditRole)
            }
        }
        
        onActiveFocusChanged: {
            // Commit changes when losing focus
            if (!activeFocus && editing) {
                editing = false
                spreadsheetModel.setData(spreadsheetModel.index, text, Qt.EditRole)
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        onDoubleClicked: {
            if (!header) {
                editing = true
                textInput.forceActiveFocus()
                textInput.selectAll()
            }
        }
    }
}