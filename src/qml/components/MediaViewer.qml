import QtQuick
import QtQuick.Controls
import QtMultimedia
import QtQuick.Window

Window {
    id: mediaWindow
    flags: Qt.Window | Qt.FramelessWindowHint
    visibility: Window.FullScreen
    color: "black"
    
    required property var mediaList
    property int currentIndex: 0
    property bool isPlaying: true
    
    // Media type detection
    function mediaType(path) {
        const ext = path.split('.').pop().toLowerCase()
        if (["jpg", "jpeg", "png", "bmp"].includes(ext)) return "image"
        if (ext === "gif") return "gif"
        if (["mp4", "mkv", "avi", "mov", "flv", "webm"].includes(ext)) return "video"
        return "unknown"
    }
    
    // Media players
    MediaPlayer {
        id: videoPlayer
        audioOutput: AudioOutput {}
        videoOutput: videoOutput
        onErrorOccurred: console.error("Video error:", errorString)
    }
    
    AnimatedImage {
        id: gifPlayer
        anchors.fill: parent
        fillMode: Image.PreserveAspectFit
        playing: mediaWindow.isPlaying
    }
    
    Image {
        id: imagePlayer
        anchors.fill: parent
        fillMode: Image.PreserveAspectFit
    }
    
    VideoOutput {
        id: videoOutput
        anchors.fill: parent
    }
    
    // Controls
    Row {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20
        z: 1
        
        Button {
            text: "◀◀"
            onClicked: mediaWindow.navigate(-1)
            visible: mediaWindow.mediaList.length > 1
        }
        
        Button {
            text: mediaWindow.isPlaying ? "❚❚" : "▶"
            onClicked: mediaWindow.togglePlay()
            visible: mediaType(mediaWindow.currentMedia) !== "image"
        }
        
        Button {
            text: "▶▶"
            onClicked: mediaWindow.navigate(1)
            visible: mediaWindow.mediaList.length > 1
        }
        
        Button {
            text: "✕"
            onClicked: mediaWindow.close()
        }
    }
    
    Text {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 10
        text: `${currentIndex+1}/${mediaList.length}`
        color: "white"
        font.pixelSize: 20
        z: 1
    }
    
    property string currentMedia: mediaList.length > 0 ? mediaList[currentIndex] : ""
    
    function navigate(direction) {
        const newIndex = (currentIndex + direction + mediaList.length) % mediaList.length
        currentIndex = newIndex
        loadMedia()
    }
    
    function togglePlay() {
        isPlaying = !isPlaying
        if (mediaType(currentMedia) === "video") {
            isPlaying ? videoPlayer.play() : videoPlayer.pause()
        }
    }
    
    function loadMedia() {
        const type = mediaType(currentMedia)
        
        if (type === "video") {
            videoPlayer.source = currentMedia
            videoPlayer.play()
            gifPlayer.visible = false
            imagePlayer.visible = false
            videoOutput.visible = true
        } 
        else if (type === "gif") {
            gifPlayer.source = currentMedia
            gifPlayer.visible = true
            imagePlayer.visible = false
            videoOutput.visible = false
        } 
        else if (type === "image") {
            imagePlayer.source = currentMedia
            gifPlayer.visible = false
            imagePlayer.visible = true
            videoOutput.visible = false
        }
    }
    
    // ADD THIS: Clean up media resources
    function cleanupMedia() {
        // Stop and reset video player
        if (videoPlayer.playbackState !== MediaPlayer.StoppedState) {
            videoPlayer.stop()
        }
        videoPlayer.source = ""
        
        // Reset GIF player
        gifPlayer.playing = false
        gifPlayer.source = ""
        
        // Reset image player
        imagePlayer.source = ""
    }
    
    // ADD THIS: Handle window closing
    onClosing: {
        cleanupMedia()
    }
    
    Component.onCompleted: loadMedia()
    Component.onDestruction: cleanupMedia() // Extra safety
    
    // Keyboard controls
    Shortcut {
        sequence: "Esc"
        onActivated: {
            cleanupMedia() // Stop media before closing
            mediaWindow.close()
        }
    }
    
    Shortcut {
        sequence: "Right"
        onActivated: navigate(1)
    }
    
    Shortcut {
        sequence: "Left"
        onActivated: navigate(-1)
    }
    
    Shortcut {
        sequence: "Space"
        onActivated: togglePlay()
    }
}