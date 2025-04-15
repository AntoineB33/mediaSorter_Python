import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    width: 400
    height: 300
    visible: true

    // Property to hold the filtered list of suggestions
    property var filteredSuggestions: []

    // Function to update the suggestions based on the TextField input
    function updateSuggestions() {
        var text = inputField.text.toLowerCase()
        if (text === "") {
            filteredSuggestions = []
            suggestionsPopup.close()
        } else {
            filteredSuggestions = allSuggestions.filter(function(item) {
                return item.toLowerCase().startsWith(text)
            })
            if (filteredSuggestions.length > 0) {
                suggestionsPopup.open()
            } else {
                suggestionsPopup.close()
            }
        }
    }

    // TextField for user input
    TextField {
        id: inputField
        width: 200
        anchors.centerIn: parent
        placeholderText: "Type something..."
        
        // Update suggestions whenever the text changes
        onTextChanged: updateSuggestions()

        // Handle key presses for navigation
        Keys.onPressed: {
            if (event.key === Qt.Key_Down && suggestionsPopup.opened) {
                suggestionsList.currentIndex = 0
                suggestionsList.forceActiveFocus()
            }
        }
    }

    // Popup to display the suggestions dropdown
    Popup {
        id: suggestionsPopup
        x: inputField.x
        y: inputField.y + inputField.height
        width: inputField.width
        height: 200
        modal: false
        focus: false
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        // ListView to display the filtered suggestions
        ListView {
            id: suggestionsList
            anchors.fill: parent
            model: filteredSuggestions
            
            delegate: ItemDelegate {
                width: parent.width
                text: modelData
                highlighted: ListView.isCurrentItem
                
                // Handle selection via mouse click
                onClicked: {
                    inputField.text = modelData
                    suggestionsPopup.close()
                    inputField.forceActiveFocus()
                }
            }

            // Handle selection via keyboard (Enter or Return key)
            Keys.onPressed: {
                if (event.key === Qt.Key_Enter || event.key === Qt.Key_Return) {
                    if (currentIndex >= 0) {
                        inputField.text = model[currentIndex]
                        suggestionsPopup.close()
                        inputField.forceActiveFocus()
                    }
                }
            }
        }
    }
}