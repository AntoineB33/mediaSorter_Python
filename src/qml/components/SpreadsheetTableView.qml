import QtQuick
import QtQuick.Controls

TableView {
    id: tableView
    model: spreadsheetModel
    clip: true

    // Initialize with enough rows/columns to make scrollbars appear
    Component.onCompleted: {
        const initRows = Math.max(spreadsheetModel.getMaxRow(), spreadsheetModel.getRenderRowCount(height))
        const initCols = Math.max(spreadsheetModel.getMaxColumn(), spreadsheetModel.getRenderColumnCount(width))
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
                var n = spreadsheetModel.getRenderRowCount(tableView.contentY + tableView.height)
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
                // Add a new column when the scrollbar reaches the end
                spreadsheetModel.addColumns(1)
            } else {
                var L = spreadsheetModel.getMaxColumn()
                var n = spreadsheetModel.getRenderColumnCount(tableView.contentX + tableView.width)
                var requiredCols = Math.max(L, n)
                var currentCols = spreadsheetModel.columnCount()
                if (requiredCols != currentCols) {
                    console.log("Setting columns to " + requiredCols)
                    spreadsheetModel.setColumns(requiredCols)
                }
            }
        }
    }

    // Cell delegate
    delegate: CellDelegate {}
}