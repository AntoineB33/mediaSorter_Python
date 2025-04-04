import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15  // Add material style
import QtQuick.Layouts 1.15

ApplicationWindow {  // Changed from Window to ApplicationWindow
    width: 300
    height: 150
    visible: true
    title: "TextField with Clear Button"
    
    // Set style to Material (or Fusion)
    Material.theme: Material.Light
    Material.accent: Material.Blue

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20

        TextField {
            id: inputField
            placeholderText: "Type something..."
            Layout.preferredWidth: 200
            font.pixelSize: 16
            padding: 10
            rightPadding: 30

            // Add clear button
            Button {
                id: clearButton
                anchors.right: parent.right
                anchors.rightMargin: 5
                anchors.verticalCenter: parent.verticalCenter
                width: 20
                height: 20
                flat: true
                text: "×"
                font.pixelSize: 18
                visible: inputField.text.length > 0
                onClicked: inputField.text = ""

                background: Rectangle {
                    color: "transparent"
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    onEntered: parent.opacity = 0.7
                    onExited: parent.opacity = 1.0
                }
            }

            // Proper background implementation
            background: Rectangle {
                implicitWidth: 200
                implicitHeight: 40
                color: inputField.enabled ? "#ffffff" : "#f6f6f6"
                border.color: inputField.activeFocus ? Material.accentColor : "#cccccc"
                border.width: 1
                radius: 5
            }
        }
    }
}