import QtQuick

Rectangle {
    implicitWidth: 100
    implicitHeight: 30
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