import QtQuick

Rectangle {
    implicitWidth: tableView.columnWidthProvider(column)
    implicitHeight: tableView.rowHeightProvider(row)
    
    Text {
        id: displayText
        anchors.fill: parent
        text: model.display
        padding: 4
        wrapMode: Text.Wrap
        visible: !editor.activeFocus
    }

    TextEdit {
        id: editor
        anchors.fill: parent
        visible: activeFocus
        text: model.display
        wrapMode: Text.Wrap
        padding: 4
        
        property TextMetrics metrics: TextMetrics {
            id: textMetrics
            font: editor.font
        }
        
        onTextChanged: {
            // Width calculation
            textMetrics.text = text
            let requiredWidth = Math.max(textMetrics.width + 10, 100)
            if (requiredWidth > tableView.columnWidthProvider(column)) {
                widthTimer.requiredWidth = requiredWidth
                widthTimer.restart()
            }
            
            // Height calculation
            let availableWidth = tableView.columnWidthProvider(column)
            let lineCount = Math.ceil(textMetrics.advanceWidth / availableWidth)
            let requiredHeight = Math.max(lineCount * 20 + 10, 30)
            if (requiredHeight > tableView.rowHeightProvider(row)) {
                heightTimer.requiredHeight = requiredHeight
                heightTimer.restart()
            }
        }

        Timer {
            id: widthTimer
            property int requiredWidth
            interval: 100
            onTriggered: spreadsheetModel.updateColumnWidth(column, requiredWidth)
        }

        Timer {
            id: heightTimer
            property int requiredHeight
            interval: 100
            onTriggered: spreadsheetModel.updateRowHeight(row, requiredHeight)
        }
    }

    MouseArea {
        anchors.fill: parent
        onDoubleClicked: editor.forceActiveFocus()
    }
}