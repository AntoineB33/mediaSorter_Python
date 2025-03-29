import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "./components" as Components

Window {
    width: 800
    height: 600
    visible: true
    title: "Dynamic Spreadsheet"

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
                const initRows = Math.max(spreadsheetModel.get_used_rows_nb(), Math.floor(height / cellHeight + 1))
                const initCols = Math.max(spreadsheetModel.get_used_cols_nb(), Math.floor(width / cellWidth + 1))
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
        width: 200
        height: 100
        color: "lightblue"
        x: tableView.x + 10  // Initial position slightly inside the TableView
        y: tableView.y + 10
        z: 1  // Ensures the floating window stays above other elements

        MouseArea {
            anchors.fill: parent
            drag.target: floatingWindow
            drag.axis: Drag.XAndYAxis
            drag.minimumX: tableView.x
            drag.maximumX: tableView.x + tableView.width - verticalScrollbar.width - floatingWindow.width
            drag.minimumY: tableView.y
            drag.maximumY: tableView.y + tableView.height - horizontalScrollbar.height - floatingWindow.height
        }

        Column {
            anchors.centerIn: parent
            spacing: 5

            RowLayout {
                spacing: 5
                TextInput {
                    id: spreadsheetNameInput
                    // Remove placeholderText and use a workaround
                    text: spreadsheetModel.currentSpreadsheetName || "Default"
                    onEditingFinished: {
                        if (text.trim() === "") {
                            text = spreadsheetModel.getDefaultSpreadsheetName();
                        }
                        spreadsheetModel.setSpreadsheetName(text);
                    }

                    // Placeholder workaround
                    Rectangle {
                        anchors.fill: parent
                        color: "transparent"
                        visible: spreadsheetNameInput.text === ""
                        Text {
                            anchors.centerIn: parent
                            text: "Enter spreadsheet name"
                            color: "gray"
                        }
                    }
                }
                Button {
                    text: "List"
                    onClicked: {
                        var names = spreadsheetModel.getSpreadsheetNames();
                        if (names.length > 0) {
                            var selectedName = names[0]; // Replace with dropdown logic
                            spreadsheetModel.loadSpreadsheet(selectedName);
                            spreadsheetNameInput.text = selectedName;
                        }
                    }
                }
            }

            Button {
                text: "Button 1"
                width: 80
            }
            Button {
                text: "Button 2"
                width: 80
            }
        }
    }

}