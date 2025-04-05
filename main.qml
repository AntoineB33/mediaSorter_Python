import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    width: 300
    height: 200
    visible: true
    title: "TextField with Dropdown"

    property var recommendations: ["Apple", "Banana", "Cherry", "Date", "Elderberry"]

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
                rightPadding: 60  // Space for both buttons
                color: "#333333"
                selectionColor: "#2196F3"

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

                onTextChanged: {
                    // Add your recommendation filtering logic here
                    dropdown.visible = text.length > 0
                }
            }

            // Clear button
            Rectangle {
                id: clearButton
                anchors {
                    right: dropdownButton.left
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
                    onClicked: {
                        inputField.text = ""
                        dropdown.visible = false
                    }
                    hoverEnabled: true
                    onEntered: parent.color = "#f0f0f0"
                    onExited: parent.color = "transparent"
                }
            }

            // Dropdown button
            Rectangle {
                id: dropdownButton
                anchors {
                    right: parent.right
                    verticalCenter: parent.verticalCenter
                    margins: 10
                }
                width: 20
                height: 20
                color: "transparent"

                Text {
                    text: "▼"
                    anchors.centerIn: parent
                    font.pixelSize: 12
                    color: "#666"
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: dropdown.visible = !dropdown.visible
                    hoverEnabled: true
                    onEntered: parent.color = "#f0f0f0"
                    onExited: parent.color = "transparent"
                }
            }

            // Dropdown list
            Rectangle {
                id: dropdown
                width: parent.width
                height: 150
                visible: false
                anchors.top: inputField.bottom
                anchors.topMargin: 5
                color: "#ffffff"
                border.color: "#cccccc"
                radius: 5

                ListView {
                    id: listView
                    anchors.fill: parent
                    anchors.margins: 5
                    clip: true
                    model: recommendations

                    delegate: Rectangle {
                        width: listView.width
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
                                dropdown.visible = false
                            }
                        }
                    }

                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }
                }
            }
        }

        // Add two buttons below the existing layout
        RowLayout {
            spacing: 10
            Layout.alignment: Qt.AlignHCenter

            Button {
                text: "Button 1"
                onClicked: console.log("Button 1 clicked")
            }

            Button {
                text: "Button 2"
                onClicked: console.log("Button 2 clicked")
            }
        }
    }
}