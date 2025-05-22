import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: floatingWindow
    property var tableView
    property var recommendations: []
    width: 300
    height: 200
    color: "lightblue"
    x: tableView.x + 10
    y: tableView.y + 10
    z: 1

    // Drag handling
    MouseArea {
        anchors.fill: parent
        drag.target: floatingWindow
        drag.axis: Drag.XAndYAxis
        drag.minimumX: 0
        drag.maximumX: mainWindow.width - floatingWindow.width - tableView.ScrollBar.vertical.width
        drag.minimumY: 0
        drag.maximumY: mainWindow.height - floatingWindow.height - tableView.ScrollBar.horizontal.height
    }

    MouseArea {
        anchors.fill: parent
        enabled: dropdown.opened
        onPressed: (mouse) => {
            console.log("Mouse pressed at:", mouse.x, mouse.y)
            // Check Popup bounds using global coordintes
            const popupLeft = dropdown.xa
            const popupRight = dropdown.x + dropdown.width
            const popupTop = dropdown.y
            const popupBottom = dropdown.y + dropdown.height
            
            // Check input field bounds using mapped coordinates
            const inputGlobal = inputField.mapToGlobal(0, 0)
            const inputLeft = inputGlobal.x
            const inputRight = inputLeft + inputField.width
            const inputTop = inputGlobal.y
            const inputBottom = inputTop + inputField.height
            
            // Test mouse position against both areas
            const inPopup = mouse.globalX >= popupLeft && mouse.globalX <= popupRight &&
                            mouse.globalY >= popupTop && mouse.globalY <= popupBottom
            
            const inInput = mouse.globalX >= inputLeft && mouse.globalX <= inputRight &&
                            mouse.globalY >= inputTop && mouse.globalY <= inputBottom

            // Close dropdown when clicking outside both areas
            if (!inPopup && !inInput) {
                dropdown.close()  // Close the dropdown
                inputField.forceActiveFocus()  // Maintain input focus
                inputField.text = spreadsheetModel.getCollectionName()
                // Removed mouse.accepted = true to allow event propagation
            }
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20

        RowLayout {
            spacing: 10
            Layout.alignment: Qt.AlignHCenter

            Button {
                text: "Rename"
                onClicked: spreadsheetModel.setCollectionName(inputField.text)
            }

            Button {
                text: "Create"
                onClicked: spreadsheetModel.createCollection(inputField.text)
            }

            Button {
                text: "Delete"
                onClicked: spreadsheetModel.deleteCollection(inputField.text)
            }
        }

        Item {
            Layout.preferredWidth: 200
            Layout.preferredHeight: 40

            TextField {
                id: inputField
                anchors.fill: parent
                placeholderText: "Type something..."
                font.pixelSize: 16
                padding: 10
                rightPadding: 40
                color: "#333333"
                selectionColor: "#2196F3"
                text: spreadsheetModel.get_collectionName()

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

                onActiveFocusChanged: {
                    if (activeFocus) {
                        dropdown.open()
                    } else if (!dropdown.activeFocus) {
                        dropdown.close()
                    }
                }

                onPressed: dropdown.open()

                onAccepted: {
                    spreadsheetModel.pressEnterOnInput(inputField.text)
                    dropdown.close();
                }
                onTextChanged: {
                    recommendations = spreadsheetModel.getOtherCollectionNames(inputField.text)
                }
            }

            // Clear button
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

            // Dropdown list using Popup
            Popup {
                id: dropdown
                // property TextField inputFieldRef: inputField
                y: inputField.height + 5
                x: inputField.x
                width: inputField.width
                height: 150
                padding: 0
                closePolicy: Popup.CloseOnEscape

                onOpened: {
                    recommendations = spreadsheetModel.getOtherCollectionNames(
                        inputField.text
                    );
                    console.log("onOpened: ", recommendations)
                }

                background: Rectangle {
                    color: "#ffffff"
                    border.color: "#cccccc"
                    radius: 5
                }

                contentItem: ListView {
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
                                inputField.forceActiveFocus();
                                spreadsheetModel.loadSpreadsheet(modelData);
                                inputField.text = modelData;
                            }
                        }
                    }
                    ScrollBar.vertical: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }
                }
            }
        }

        // Buttons
        RowLayout {
            spacing: 10
            Layout.alignment: Qt.AlignHCenter

            Button {
                text: "Sort"
                // onClicked: spreadsheetModel.findSortings()
            }

            Button {
                text: "Button 2"
            }
        }
    }
}