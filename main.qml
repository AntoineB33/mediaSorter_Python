import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    width: 300
    height: 150
    visible: true
    title: "TextField with Clear Button"

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20

        Item {
            Layout.preferredWidth: 200
            Layout.preferredHeight: 40

            TextField {
                id: inputField
                anchors.fill: parent
                placeholderText: "Type something..."
                font.pixelSize: 16
                padding: 10
                rightPadding: 30
    
                // Universal text properties
                color: "#333333"  // Text color
                selectionColor: "#2196F3"  // Only use universally supported properties

                // Custom cursor implementation
                cursorDelegate: Rectangle {
                    visible: inputField.cursorVisible
                    color: "#2196F3"
                    width: 2
                    height: inputField.font.pixelSize + 4
                    y: 2
                }

                background: Rectangle {
                    color: "#ffffff"
                    border.color: inputField.activeFocus ? "#2196F3" : "#cccccc"
                    border.width: 1
                    radius: 5
                }
            }

            Rectangle {
                id: clearButton
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
                    cursorShape: Qt.PointingHandCursor
                    onClicked: inputField.text = ""
                    hoverEnabled: true
                    onEntered: parent.color = "#f0f0f0"
                    onExited: parent.color = "transparent"
                }
            }
        }
    }
}