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
            const initRows = Math.max(spreadsheetModel.rowCount(), Math.ceil(height / cellHeight + 1))
            const initCols = Math.max(spreadsheetModel.columnCount(), Math.ceil(width / cellWidth + 1))
            spreadsheetModel.addRows(initRows)
            spreadsheetModel.addColumns(initCols)
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
                        console.log("requiredCols : "+requiredCols+" currentCols : "+currentCols)
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
                onEditingFinished: {
                    console.log("Editing finished. New text: " + text)
                    // Ensure the model is updated
                    var modelIndex = tableView.model.index(model.row, model.column)
                    // Pass value and EditRole as arguments
                    var success = spreadsheetModel.setData(modelIndex, text, Qt.EditRole)
                    if (!success) {
                        console.error("Failed to update model data at index: " + model.index)
                    }
                }
            }
        }
    }
}