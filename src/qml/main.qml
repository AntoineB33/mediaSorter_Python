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

        // Vertical Header (Row Numbers)
        ListView {
            id: rowHeader
            Layout.preferredWidth: 40
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
                    text: index + 1  // Show 1-based index
                    anchors.centerIn: parent
                    font.pixelSize: 12
                }
            }

            // Synchronize vertical scrolling with TableView
            contentY: tableView.contentY

            // Update model when rows are added/removed
            Connections {
                target: spreadsheetModel
                function onRowsInserted(parent, first, last) { 
                    rowHeader.model = spreadsheetModel.rowCount() 
                }
                function onRowsRemoved(parent, first, last) { 
                    rowHeader.model = spreadsheetModel.rowCount() 
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
                const initRows = Math.max(spreadsheetModel.get_used_rows_nb(), Math.ceil(height / cellHeight + 1))
                const initCols = Math.max(spreadsheetModel.get_used_cols_nb(), Math.ceil(width / cellWidth + 1))
                spreadsheetModel.setRows(initRows)
                spreadsheetModel.setColumns(initCols)
                console.log("Initialized with rows: " + initRows + ", columns: " + initCols)
            }

            // Handle Shift + Wheel for horizontal scrolling
            MouseArea {
                anchors.fill: parent
                propagateComposedEvents: true
                
                onWheel: function(wheel) {
                    if (wheel.modifiers & Qt.ShiftModifier) {
                        // Calculate horizontal scroll amount
                        const delta = wheel.angleDelta.y + wheel.angleDelta.x;
                        const step = delta / 120; // Normalize wheel steps
                        
                        // Update horizontal scrollbar position
                        horizontalScrollbar.position = Math.max(0,
                            Math.min(1 - horizontalScrollbar.size, 
                            horizontalScrollbar.position - step * 0.1));
                        
                        // Trigger position change handler
                        horizontalScrollbar.positionChanged();
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
                        spreadsheetModel.addColumns(1)
                    } else {
                        var L = spreadsheetModel.getMaxColumn()
                        var n = Math.floor((tableView.contentX + tableView.width) / tableView.cellWidth + 1)
                        var requiredCols = Math.max(L + 1, n)
                        var currentCols = spreadsheetModel.columnCount()
                        if (requiredCols != currentCols) {
                            console.log("requiredCols : "+requiredCols+" currentCols : "+currentCols)
                            spreadsheetModel.setColumns(requiredCols)
                        }
                    }
                }
            }

            // Cell delegate
            delegate: Components.CellDelegate {}
        }
    }

}