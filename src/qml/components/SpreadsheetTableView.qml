import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TableView {
    id: tableView
    Layout.fillWidth: true
    Layout.fillHeight: true
    model: spreadsheetModel
    clip: true

    // Fixed cell dimensions (no recursive bindings)
    property real cellWidth: 100
    property real cellHeight: 30
    
    // Replace existing cellWidth/cellHeight properties with:
    property Timer layoutTimer: Timer {
        interval: 0
        onTriggered: tableView.forceLayout()
    }

    Connections {
        target: spreadsheetModel
        function onColumn_width_changed() { layoutTimer.restart() }
        function onRow_height_changed() { layoutTimer.restart() }
    }

    // Initialize with enough rows/columns to make scrollbars appear
    Component.onCompleted: {
        const initRows = Math.max(spreadsheetModel.getMaxRow(), Math.floor(height / cellHeight + 1))
        const initCols = Math.max(spreadsheetModel.getMaxColumn(), Math.floor(width / cellWidth + 1))
        spreadsheetModel.setRows(initRows)
        spreadsheetModel.setColumns(initCols)

        // Trigger initial scroll update after layout
        Qt.callLater(function() {
            // Vertical scroll initial values
            spreadsheetModel.verticalScroll(verticalScrollbar.position, verticalScrollbar.size, tableView.contentY, tableView.height, true)
            // Horizontal scroll initial values
            spreadsheetModel.horizontalScroll(horizontalScrollbar.position, horizontalScrollbar.size, tableView.contentX, tableView.width, true)
        })
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
            spreadsheetModel.verticalScroll(position, size, tableView.contentY, tableView.height, false)
        }
    }

    // Horizontal scrollbar
    ScrollBar.horizontal: ScrollBar {
        id: horizontalScrollbar
        policy: ScrollBar.AlwaysOn

        onPositionChanged: {
            spreadsheetModel.horizontalScroll(position, size, tableView.contentX, tableView.width, false)
        }
    }

    // Cell delegate
    delegate: CellDelegate {}
}