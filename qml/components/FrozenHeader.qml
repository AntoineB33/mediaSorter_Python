// qml/components/FrozenHeader.qml
ListView {
    id: header
    orientation: ListView.Horizontal
    interactive: false
    model: parent.model
    
    delegate: Rectangle {
        width: 100
        height: 30
        border.width: 1
        Text {
            text: model.headerData(model.column, Qt.Horizontal)
        }
    }
    
    // Sync horizontal scroll with main view
    Connections {
        target: syncView
        function onContentXChanged() {
            header.contentX = syncView.contentX
        }
    }
}