import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TableView {
    id: root
    clip: true

    property real cellWidth: 100
    property real cellHeight: 30
    property var spreadsheetModel

    ScrollBar.vertical: ScrollBar {
        id: verticalScrollbar
        policy: ScrollBar.AlwaysOn
        onPositionChanged: handleVerticalScroll()
    }

    ScrollBar.horizontal: ScrollBar {
        id: horizontalScrollbar
        policy: ScrollBar.AlwaysOn
        onPositionChanged: handleHorizontalScroll()
    }

    MouseArea {
        anchors.fill: parent
        propagateComposedEvents: true
        onWheel: handleShiftScroll(wheel)
    }

    function handleVerticalScroll() {
        if (position >= 1.0 - size) {
            spreadsheetModel.addRows(1)
        } else {
            const requiredRows = Math.max(
                spreadsheetModel.getMaxRow(),
                Math.floor((contentY + height) / cellHeight + 1)
            )
            if (requiredRows !== spreadsheetModel.rowCount()) {
                spreadsheetModel.setRows(requiredRows)
            }
        }
    }

    function handleHorizontalScroll() {
        if (position >= 1.0 - size) {
            spreadsheetModel.addColumns(1)
        } else {
            const requiredCols = Math.max(
                spreadsheetModel.getMaxColumn(),
                Math.floor((contentX + width) / cellWidth + 1)
            )
            if (requiredCols !== spreadsheetModel.columnCount()) {
                spreadsheetModel.setColumns(requiredCols)
            }
        }
    }

    function handleShiftScroll(wheel) {
        if (wheel.modifiers & Qt.ShiftModifier) {
            const step = wheel.angleDelta.y / Math.abs(wheel.angleDelta.y) * 0.1
            horizontalScrollbar.position = Math.max(0,
                Math.min(1 - horizontalScrollbar.size,
                horizontalScrollbar.position - step))
            wheel.accepted = true
        } else {
            wheel.accepted = false
        }
    }
}