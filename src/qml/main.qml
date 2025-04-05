import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "./components" as Components

Window {
    width: 800
    height: 600
    visible: true
    title: "Dynamic Spreadsheet"
    property var recommendations: ["Apple", "Banana", "Cherry", "Date", "Elderberry"]

    RowLayout {
        anchors.fill: parent
        spacing: 0


        ListView {
            id: rowHeader
            Layout.preferredWidth: 40
            Layout.fillHeight: true  // Add this line
            model: spreadsheetModel.rowCount()
            boundsBehavior: Flickable.StopAtBounds
            interactive: false
            clip: true

            delegate: Rectangle {
                width: rowHeader.width
                height: tableView.cellHeight
                color: "#f0f0f0"
                border.color: "#cccccc"
                
                Text {
                    text: index + 1
                    anchors.centerIn: parent
                    font.pixelSize: 12
                }
            }

            contentY: tableView.contentY

            Connections {
                target: spreadsheetModel
                function onRowsInserted(parent, first, last) { 
                    rowHeader.model = spreadsheetModel.rowCount(); 
                }
                function onRowsRemoved(parent, first, last) { 
                    rowHeader.model = spreadsheetModel.rowCount(); 
                }
            }
        }

        TableView {
            id: tableView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: spreadsheetModel
            clip: true

            // Fixed cell dimensions (no recursive bindings)
            property real cellWidth: 100
            property real cellHeight: 30

            // Initialize with enough rows/columns to make scrollbars appear
            Component.onCompleted: {
                const initRows = Math.max(spreadsheetModel.getMaxRow(), Math.floor(height / cellHeight + 1))
                const initCols = Math.max(spreadsheetModel.getMaxColumn(), Math.floor(width / cellWidth + 1))
                spreadsheetModel.setRows(initRows)
                spreadsheetModel.setColumns(initCols)
            }

            // Handle Shift + Wheel for horizontal scrolling
            MouseArea {
                anchors.fill: parent
                propagateComposedEvents: true
                
                onWheel: function(wheel) {
                    if (wheel.modifiers & Qt.ShiftModifier) {
                        // Use vertical wheel movement for horizontal scrolling when Shift is pressed
                        const delta = wheel.angleDelta.y;
                        // Normalize and scale the scroll amount
                        const step = delta / Math.abs(delta) * 0.1; // 0.1 is the scroll speed factor
                        
                        // Calculate new position with bounds checking
                        horizontalScrollbar.position = Math.max(0,
                            Math.min(1 - horizontalScrollbar.size,
                            horizontalScrollbar.position - step));
                        wheel.accepted = true;
                    } else {
                        wheel.accepted = false; // Allow vertical scrolling
                    }
                }
            }

            // Vertical scrollbar
            ScrollBar.vertical: ScrollBar {
                id: verticalScrollbar
                policy: ScrollBar.AlwaysOn

                onPositionChanged: {
                    if (position >= 1.0 - size) {
                        spreadsheetModel.addRows(1)
                    } else {
                        var L = spreadsheetModel.getMaxRow()
                        var n = Math.floor((tableView.contentY + tableView.height) / tableView.cellHeight + 1)
                        var requiredRows = Math.max(L + 1, n)
                        var currentRows = spreadsheetModel.rowCount()
                        if (requiredRows != currentRows) {
                            spreadsheetModel.setRows(requiredRows)
                        }
                    }
                }
            }

            // Horizontal scrollbar
            ScrollBar.horizontal: ScrollBar {
                id: horizontalScrollbar
                policy: ScrollBar.AlwaysOn

                onPositionChanged: {
                    if (position >= 1.0 - size) {
                        // Add a new column when the scrollbar reaches the end
                        spreadsheetModel.addColumns(1)
                    } else {
                        var L = spreadsheetModel.getMaxColumn()
                        var n = Math.floor((tableView.contentX + tableView.width) / tableView.cellWidth + 1)
                        var requiredCols = Math.max(L + 1, n)
                        var currentCols = spreadsheetModel.columnCount()
                        if (requiredCols != currentCols) {
                            console.log("Setting columns to " + requiredCols)
                            spreadsheetModel.setColumns(requiredCols)
                        }
                    }
                }
            }

            // Cell delegate
            delegate: Components.CellDelegate {}
        }
    }

    Rectangle {
        id: floatingWindow
        width: 300
        height: 200
        color: "lightblue"
        x: tableView.x + 10
        y: tableView.y + 10
        z: 1


        MouseArea {
            anchors.fill: parent
            drag.target: floatingWindow
            drag.axis: Drag.XAndYAxis
            drag.minimumX: tableView.x
            drag.maximumX: tableView.x + tableView.width - verticalScrollbar.width - floatingWindow.width
            drag.minimumY: tableView.y
            drag.maximumY: tableView.y + tableView.height - horizontalScrollbar.height - floatingWindow.height
        }

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
            }

            // Dropdown list using Popup
            Popup {
                id: dropdown
                y: inputField.height + 5  // Position below the TextField
                x: inputField.x
                width: inputField.width
                height: 150
                padding: 0
                visible: false

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

}