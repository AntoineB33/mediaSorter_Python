import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property alias text: inputField.text
    property var recommendations: []
    property var spreadsheetModel
    
    width: 200
    height: 40

    TextField {
        id: inputField
        anchors.fill: parent
        placeholderText: "Type something..."
        font.pixelSize: 16
        padding: 10
        rightPadding: 40
        text: spreadsheetModel.input_text

        background: Rectangle {
            color: "#ffffff"
            border.color: inputField.activeFocus ? "#2196F3" : "#cccccc"
            border.width: 1
            radius: 5
        }

        onActiveFocusChanged: {
            if (activeFocus) dropdown.open()
            else if (!dropdown.activeFocus) dropdown.close()
        }

        onPressed: dropdown.open()
        onAccepted: {
            spreadsheetModel.pressEnterOnInput(text)
            dropdown.close()
        }
    
        // Add explicit property binding
        Binding {
            target: inputField
            property: "text"
            value: spreadsheetModel.input_text
            when: !inputField.activeFocus
        }
        onTextChanged: recommendations = spreadsheetModel.getOtherCollectionNames(text)
    }

    Rectangle {  // Clear button
        anchors {
            right: parent.right
            verticalCenter: parent.verticalCenter
            margins: 10
        }
        width: 20
        height: 20
        color: "transparent"
        visible: inputField.text.length > 0

        Text {
            text: "×"
            anchors.centerIn: parent
            font.pixelSize: 18
            color: "#666"
        }

        MouseArea {
            anchors.fill: parent
            onClicked: inputField.text = ""
            hoverEnabled: true
            onEntered: parent.color = "#f0f0f0"
            onExited: parent.color = "transparent"
        }
    }

    Popup {  // Dropdown
        id: dropdown
        y: inputField.height + 5
        width: inputField.width
        height: 150
        padding: 0
        closePolicy: Popup.CloseOnEscape

        background: Rectangle {
            color: "#ffffff"
            border.color: "#cccccc"
            radius: 5
        }

        contentItem: ListView {
            anchors.fill: parent
            anchors.margins: 5
            clip: true
            model: root.recommendations

            delegate: Rectangle {
                width: parent.width
                height: 30
                color: mouseArea.containsMouse ? "#f0f0f0" : "transparent"

                Text {
                    text: modelData
                    anchors.verticalCenter: parent.verticalCenter
                    leftPadding: 10
                    font.pixelSize: 14
                    color: "#333333"
                }

                MouseArea {
                    id: mouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        inputField.text = modelData
                        spreadsheetModel.loadSpreadsheet(modelData)
                    }
                }
            }

            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        }
    }
}