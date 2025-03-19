import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    width: 800
    height: 600
    visible: true
    title: "Dynamic Spreadsheet"

    TableView {
        id: tableView
        anchors.fill: parent
        model: spreadsheetModel
        clip: true

        property real cellWidth: 100
        property real cellHeight: 30

        // Initialize with enough rows/columns to make scrollbars appear
        Component.onCompleted: {
            const initRows = Math.ceil(height / cellHeight) + 2
            const initCols = Math.ceil(width / cellWidth) + 2
            spreadsheetModel.addRows(initRows)
            spreadsheetModel.addColumns(initCols)
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
                    var requiredRows = Math.max(L, n)
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
                    var requiredCols = Math.max(L, n)
                    var currentCols = spreadsheetModel.columnCount()
                    if (requiredCols != currentCols) {
                        spreadsheetModel.setColumns(requiredCols)
                    }
                }
            }
        }

        // Cell delegate
        delegate: Rectangle {
            implicitWidth: tableView.cellWidth
            implicitHeight: tableView.cellHeight
            border.color: "lightgray"

            TextInput {
                anchors.fill: parent
                anchors.margins: 2
                text: model.display
                onEditingFinished: model.display = text
            }
        }
    }
}