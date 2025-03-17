import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

TableView {
    id: tableView
    clip: true
    
    model: infiniteModel
    columnWidthProvider: columnWidthFunc
    rowHeightProvider: rowHeightFunc
    
    // Frozen header
    Item {
        id: headerContainer
        width: tableView.width
        height: 30
        z: 2
        
        ListView {
            id: headerView
            orientation: ListView.Horizontal
            model: tableView.columns > 0 ? tableView.columns : 1
            spacing: 1
            interactive: false
            contentX: tableView.contentX
            
            delegate: Rectangle {
                width: tableView.columnWidthProvider(modelData)
                height: 30
                color: infiniteModel.getColumnColor(modelData)
                
                TextInput {
                    text: infiniteModel.data(infiniteModel.index(0, modelData), Qt.DisplayRole)
                    anchors.fill: parent
                    verticalAlignment: Text.AlignVCenter
                    onEditingFinished: infiniteModel.setData(infiniteModel.index(0, modelData), text)
                }
            }
        }
    }
    
    delegate: Rectangle {
        border.width: 1
        color: model.background
        
        TextInput {
            text: model.display
            anchors.fill: parent
            verticalAlignment: Text.AlignVCenter
            onEditingFinished: infiniteModel.setData(infiniteModel.index(row, column), text)
        }
    }
    
    function columnWidthFunc(column) { return 100 }
    function rowHeightFunc(row) { return 30 }
    
    Connections {
        target: infiniteModel
        function onColumnColorChanged(col, color) {
            tableView.forceLayout()
        }
    }
}