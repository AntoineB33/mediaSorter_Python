import QtQuick
import QtQuick.Controls

Window {
    id: control
    flags: Qt.ToolTip
    color: "lightgray"
    visible: true
    
    property var currentColumn: -1
    
    Column {
        spacing: 5
        padding: 10
        
        Button {
            text: "Play"
            onClicked: controller.playClicked()
        }
        
        Button {
            text: "Sort"
            onClicked: controller.sortClicked()
        }
        
        ComboBox {
            id: roleSelector
            model: ["Condition", "Tag", "Name"]
            onActivated: {
                if(currentColumn >= 0) {
                    controller.changeColumnColor(currentColumn, index)
                }
            }
        }
    }
    
    // Draggable functionality
    DragHandler {
        target: control
    }
}