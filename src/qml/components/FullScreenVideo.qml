import QtQuick
import QtQuick.Window
import QtMultimedia

Window {
    id: videoWindow
    flags: Qt.Window | Qt.FramelessWindowHint
    visibility: Window.FullScreen
    color: "black"

    required property url videoSource

    MediaPlayer {
        id: mediaPlayer
        source: videoWindow.videoSource
        videoOutput: videoOutput
        audioOutput: AudioOutput {}
        loops: MediaPlayer.Infinite
    }

    VideoOutput {
        id: videoOutput
        anchors.fill: parent
    }

    // Close on ESC key
    Shortcut {
        sequence: "Esc"
        onActivated: videoWindow.close()
    }

    // Close on click
    MouseArea {
        anchors.fill: parent
        onClicked: videoWindow.close()
    }

    Component.onCompleted: mediaPlayer.play()
    onClosing: mediaPlayer.stop()
}