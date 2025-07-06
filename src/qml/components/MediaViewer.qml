import QtQuick
import QtQuick.Controls
import QtMultimedia
import QtQuick.Window

Window {
    id: mediaWindow
    flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
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
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        playing: mediaWindow.isPlaying
        
        // Set explicit size to natural size or scaled down
        property real scaleFactor: Math.min(1, 
            Math.min(parent.width / implicitWidth, parent.height / implicitHeight))
        width: implicitWidth * scaleFactor
        height: implicitHeight * scaleFactor
    }
    
    Image {
        id: imagePlayer
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        
        // Set explicit size to natural size or scaled down
        property real scaleFactor: Math.min(1, 
            Math.min(parent.width / implicitWidth, parent.height / implicitHeight))
        width: implicitWidth * scaleFactor
        height: implicitHeight * scaleFactor
    }
    
    VideoOutput {
        id: videoOutput
        anchors.centerIn: parent
        fillMode: VideoOutput.PreserveAspectFit
        
        // Set explicit size to natural size or scaled down
        property real scaleFactor: {
            if (!videoPlayer.metaData.resolution) return 1
            const vidWidth = videoPlayer.metaData.resolution.width
            const vidHeight = videoPlayer.metaData.resolution.height
            return Math.min(1, 
                Math.min(parent.width / vidWidth, parent.height / vidHeight))
        }
        width: videoPlayer.metaData.resolution ? 
            videoPlayer.metaData.resolution.width * scaleFactor : parent.width
        height: videoPlayer.metaData.resolution ? 
            videoPlayer.metaData.resolution.height * scaleFactor : parent.height
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
            enabled: currentIndex > 0
            opacity: enabled ? 1 : 0.5
        }
        
        Button {
            text: mediaWindow.isPlaying ? "❚❚" : "▶"
            onClicked: mediaWindow.togglePlay()
            visible: mediaType(mediaWindow.currentMedia) !== "image"
        }
        
        Button {
            text: "▶▶"
            onClicked: mediaWindow.navigate(1)
            enabled: currentIndex < mediaList.length - 1
            opacity: enabled ? 1 : 0.5
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
        const newIndex = currentIndex + direction
        
        // Boundary checks - don't navigate beyond first/last
        if (newIndex < 0 || newIndex >= mediaList.length) {
            return
        }
        
        // Clean up current media before changing
        cleanupMedia()
        
        currentIndex = newIndex
        loadMedia()
    }
    
    function togglePlay() {
        isPlaying = !isPlaying
        
        const type = mediaType(currentMedia)
        if (type === "video") {
            isPlaying ? videoPlayer.play() : videoPlayer.pause()
        }
        else if (type === "gif") {
            gifPlayer.playing = isPlaying
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
            isPlaying = true
        } 
        else if (type === "gif") {
            gifPlayer.source = currentMedia
            gifPlayer.visible = true
            imagePlayer.visible = false
            videoOutput.visible = false
            isPlaying = true
        } 
        else if (type === "image") {
            imagePlayer.source = currentMedia
            gifPlayer.visible = false
            imagePlayer.visible = true
            videoOutput.visible = false
            isPlaying = false
        }
    }
    
    // Clean up media resources
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
    
    // Handle window closing
    onClosing: {
        cleanupMedia()
    }
    
    Component.onCompleted: {
        visibility = Window.FullScreen
        requestActivate()
        raise()
        loadMedia()
    }
    
    Component.onDestruction: cleanupMedia()
    
    // Keyboard controls
    Shortcut {
        sequence: "Esc"
        onActivated: {
            cleanupMedia()
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