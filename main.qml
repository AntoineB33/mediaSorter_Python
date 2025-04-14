import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    visible: true
    width: 400
    height: 200
    title: "QML AutoComplete"

    ColumnLayout {
        anchors.fill: parent
        padding: 20

        TextField {
            id: textInput
            Layout.fillWidth: true
            placeholderText: "Type a fruit name..."
            
            onTextChanged: {
                suggestionHandler.update_suggestions(text)
            }
        }

        Rectangle {
            id: suggestionBox
            Layout.fillWidth: true
            height: 200
            visible: suggestionHandler.suggestions.length > 0
            color: "white"
            border.color: "lightgray"
            radius: 2
            
            ListView {
                id: listView
                anchors.fill: parent
                clip: true
                model: suggestionHandler.suggestions
                
                delegate: ItemDelegate {
                    width: listView.width
                    text: modelData
                    
                    onClicked: {
                        textInput.text = modelData
                        suggestionHandler.update_suggestions("")
                    }
                }
                
                ScrollBar.vertical: ScrollBar {}
            }
        }
    }
}