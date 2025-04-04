import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Window {
    width: 300
    height: 150
    visible: true
    title: "TextField with Clear Button"

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20

        TextField {
            id: inputField
            placeholderText: "Type something..."
            Layout.preferredWidth: 200
            font.pixelSize: 16
            padding: 10
            rightPadding: 30  // Make space for the X button

            // Clear button implementation
            Text {
                id: clearButton
                anchors {
                    verticalCenter: parent.verticalCenter
                    right: parent.right
                    rightMargin: 10
                }
                text: "×"
                font.pixelSize: 20
                color: "#666"
                visible: inputField.text.length > 0

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        inputField.text = ""
                        inputField.forceActiveFocus()
                    }
                }

                // Hover effects
                states: [
                    State {
                        name: "hovered"
                        when: clearButtonMouse.containsMouse
                        PropertyChanges {
                            target: clearButton
                            color: "#333"
                            scale: 1.1
                        }
                    },
                    State {
                        name: "pressed"
                        when: clearButtonMouse.pressed
                        PropertyChanges {
                            target: clearButton
                            color: "#000"
                            scale: 0.9
                        }
                    }
                ]

                HoverHandler {
                    id: clearButtonMouse
                    cursorShape: Qt.PointingHandCursor
                }

                Behavior on color { ColorAnimation { duration: 100 } }
                Behavior on scale { NumberAnimation { duration: 100 } }
            }

            // Custom background
            background: Rectangle {
                color: "#f0f0f0"
                border.color: inputField.activeFocus ? "#2196F3" : "#ccc"
                border.width: 1
                radius: 5
            }
        }
    }
}