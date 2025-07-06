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
        
        // Video position and duration
        property real videoDuration: duration > 0 ? duration : 1
        property real frameDuration: {
            if (metaData.videoFrameRate) return 1000 / metaData.videoFrameRate
            if (metaData.pixelAspectRatio) return 1000 / 30 // Fallback to 30fps
            return 33.33 // Default to 30fps
        }
    }
    
    AnimatedImage {
        id: gifPlayer
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        playing: mediaWindow.isPlaying
        
        property real scaleFactor: Math.min(1, 
            Math.min(parent.width / implicitWidth, parent.height / implicitHeight))
        width: implicitWidth * scaleFactor
        height: implicitHeight * scaleFactor
    }
    
    Image {
        id: imagePlayer
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        
        property real scaleFactor: Math.min(1, 
            Math.min(parent.width / implicitWidth, parent.height / implicitHeight))
        width: implicitWidth * scaleFactor
        height: implicitHeight * scaleFactor
    }
    
    VideoOutput {
        id: videoOutput
        anchors.centerIn: parent
        fillMode: VideoOutput.PreserveAspectFit
        
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
    
    // Video navigation functions
    function seekVideo(seconds) {
        if (mediaType(currentMedia) !== "video") return
        
        const newPosition = Math.max(0, Math.min(
            videoPlayer.position + (seconds * 1000), 
            videoPlayer.duration
        ))
        videoPlayer.setPosition(newPosition)
    }
    
    function seekToFraction(fraction) {
        if (mediaType(currentMedia) !== "video") return
        
        const newPosition = Math.max(0, Math.min(
            videoPlayer.duration * fraction, 
            videoPlayer.duration
        ))
        videoPlayer.setPosition(newPosition)
    }
    
    function stepFrames(direction) {
        if (mediaType(currentMedia) !== "video") return
        
        // Pause video before stepping frames
        if (videoPlayer.playbackState === MediaPlayer.PlayingState) {
            videoPlayer.pause()
            mediaWindow.isPlaying = false
        }
        
        // Calculate frame duration dynamically
        let frameDuration = 40 // Default to 25fps (1000/25=40ms)
        if (videoPlayer.metaData.videoFrameRate) {
            frameDuration = 1000 / videoPlayer.metaData.videoFrameRate
        }
        
        const frameMs = direction * frameDuration
        const newPosition = Math.max(0, Math.min(
            videoPlayer.position + frameMs, 
            videoPlayer.duration
        ))
        videoPlayer.setPosition(newPosition)
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
    
    // Add new video navigation shortcuts
    Shortcut {
        sequence: "U"
        onActivated: seekVideo(-5) // 5 seconds backward
    }
    
    Shortcut {
        sequence: "O"
        onActivated: seekVideo(5) // 5 seconds forward
    }
    
    Shortcut {
        sequence: "J"
        onActivated: seekVideo(-10) // 10 seconds backward
    }
    
    Shortcut {
        sequence: "L"
        onActivated: seekVideo(10) // 10 seconds forward
    }
    
    Shortcut {
        sequence: ","
        onActivated: stepFrames(-1) // One frame backward
    }
    
    Shortcut {
        sequence: "."
        onActivated: stepFrames(1) // One frame forward
    }
    
    // Number keys for fraction navigation (1-9)
    Shortcut {
        sequence: "1"
        onActivated: seekToFraction(0.1) // 1/10 of video
    }
    
    Shortcut {
        sequence: "2"
        onActivated: seekToFraction(0.2) // 2/10 of video
    }
    
    Shortcut {
        sequence: "3"
        onActivated: seekToFraction(0.3) // 3/10 of video
    }
    
    Shortcut {
        sequence: "4"
        onActivated: seekToFraction(0.4) // 4/10 of video
    }
    
    Shortcut {
        sequence: "5"
        onActivated: seekToFraction(0.5) // 5/10 of video
    }
    
    Shortcut {
        sequence: "6"
        onActivated: seekToFraction(0.6) // 6/10 of video
    }
    
    Shortcut {
        sequence: "7"
        onActivated: seekToFraction(0.7) // 7/10 of video
    }
    
    Shortcut {
        sequence: "8"
        onActivated: seekToFraction(0.8) // 8/10 of video
    }
    
    Shortcut {
        sequence: "9"
        onActivated: seekToFraction(0.9) // 9/10 of video
    }
    
    Shortcut {
        sequence: "0"
        onActivated: seekToFraction(0) // Beginning of video
    }
}