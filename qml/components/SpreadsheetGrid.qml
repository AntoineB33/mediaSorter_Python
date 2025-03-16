import QtQuick
import QtQuick.Controls

TableView {
    id: root
    clip: true
    columnSpacing: 1
    rowSpacing: 1
    
    // Connect to Python model
    model: tableModel

    // Frozen row implementation
    topMargin: frozenHeader.height
    FrozenHeader {
        id: frozenHeader
        width: parent.width
        model: root.model
        syncView: root
    }

    delegate: Rectangle {
        border.width: 1
        TextInput {
            anchors.fill: parent
            text: display
            onEditingFinished: {
                // Update Python model
                root.model.setData(index, text)
            }
        }
    }
}