import pygame
import os
import sys
import tempfile
import subprocess
import threading
import time
from PIL import Image
import cv2
import numpy as np
import logging

# Set up logging
logging.basicConfig(filename='media_viewer.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Add this function to get the path to ffmpeg with better error handling
def get_ffmpeg_path():
    # First try system PATH
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            logging.info("FFmpeg found in system PATH")
            return "ffmpeg"
    except Exception:
        pass
    
    # Try local bin directory (relative to this script)
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bin_dir = os.path.join(script_dir, "bin")
        ffmpeg_path = os.path.join(bin_dir, "ffmpeg.exe")

        if os.path.exists(ffmpeg_path):
            logging.info(f"FFmpeg found in local bin directory: {ffmpeg_path}")
            return ffmpeg_path
    except Exception as e:
        logging.error(f"Error checking local bin directory: {e}")
    
    # Try current working directory
    try:
        if os.path.exists("ffmpeg.exe"):
            logging.info("FFmpeg found in current directory")
            return "ffmpeg.exe"
    except Exception:
        pass
    
    logging.warning("FFmpeg not found in any location")
    return None

def load_and_scale_image(self, image_path, screen_width, screen_height):
    try:
        image = pygame.image.load(image_path)
        if image.get_alpha() is not None:
            image = image.convert_alpha()
        else:
            image = image.convert()
        image_width, image_height = image.get_size()
        
        scale_factor = min(
            1.0,
            min(screen_width / image_width, screen_height / image_height)
        )
        new_width = int(image_width * scale_factor)
        new_height = int(image_height * scale_factor)
        
        if scale_factor < 1.0:
            scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
        else:
            scaled_image = image
        return scaled_image
    except Exception as e:
        logging.error(f"Error loading image {image_path}: {e}")
        return None

def load_gif_frames(image_path, screen_width, screen_height):
    frames = []
    durations = []
    try:
        img = Image.open(image_path)
        while True:
            frame = img.convert("RGBA")
            img_width, img_height = frame.size
            scale_factor = min(
                1.0,
                min(screen_width / img_width, screen_height / img_height)
            )
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            frame = frame.resize((new_width, new_height), Image.LANCZOS)
            mode = frame.mode
            data = frame.tobytes()
            surface = pygame.image.fromstring(data, frame.size, mode)
            frames.append(surface)
            durations.append(img.info.get('duration', 100))
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    except Exception as e:
        logging.error(f"Error loading GIF {image_path}: {e}")
    return frames, durations

def seek_video(video_cap, seconds, fps, audio_playing, audio_ready, video_paused):
    current_time = video_cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    new_time = max(0, current_time + seconds)
    video_cap.set(cv2.CAP_PROP_POS_MSEC, new_time * 1000)
    
    if audio_playing and audio_ready:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.play(0, new_time)
            if video_paused:
                pygame.mixer.music.pause()
        except Exception as e:
            logging.error(f"Error seeking audio: {e}")

def step_frame(video_cap, step, fps, audio_playing, audio_ready, video_paused):
    current_frame = video_cap.get(cv2.CAP_PROP_POS_FRAMES)
    new_frame = max(0, current_frame + step)
    video_cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
    
    if audio_playing and audio_ready:
        new_time = new_frame / fps
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.play(0, new_time)
            if video_paused:
                pygame.mixer.music.pause()
        except Exception as e:
            logging.error(f"Error stepping audio: {e}")

def show_images(self, image_paths):
    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    
    # Get display info
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    
    # Create borderless window
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Image Viewer")

    VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".webm"]
    
    # Load media
    scaled_images = []
    gif_infos = []
    media_types = []
    video_paths = []
    audio_threads = []
    audio_files = []
    audio_ready = [False] * len(image_paths)
    
    # Get ffmpeg path
    ffmpeg_path = get_ffmpeg_path()
    ffmpeg_available = ffmpeg_path is not None
    
    if not ffmpeg_available:
        logging.warning("FFmpeg not found. Videos will play without audio.")
        print("Warning: FFmpeg not found. Videos will play without audio.")
    
    for i, path in enumerate(image_paths):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".gif":
            frames, durations = load_gif_frames(path, screen_width, screen_height)
            if frames:
                scaled_images.append(frames[0])
                gif_infos.append((frames, durations))
                media_types.append("gif")
                video_paths.append(None)
                audio_files.append(None)
            else:
                scaled_images.append(None)
                gif_infos.append(None)
                media_types.append("image")
                video_paths.append(None)
                audio_files.append(None)
        elif ext in VIDEO_EXTENSIONS:  # Now checks against all video extensions
            scaled_images.append(None)
            gif_infos.append(None)
            media_types.append("video")
            video_paths.append(path)
            
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile:
                audio_path = tmpfile.name
            audio_files.append(audio_path)
            
            # Only extract audio if ffmpeg is available
            if ffmpeg_available:
                # Start audio extraction in background thread
                def extract_audio(video_path, audio_path, ffmpeg_path, index):
                    try:
                        logging.info(f"Starting audio extraction for {video_path}")
                        cmd = [
                            ffmpeg_path,
                            '-y',  # Overwrite output
                            '-i', f'"{video_path}"',  # Quote paths to handle spaces
                            '-vn',  # No video
                            '-acodec', 'pcm_s16le',
                            '-ar', '44100',
                            '-ac', '2',
                            f'"{audio_path}"'
                        ]
                        
                        # Print the command for debugging
                        cmd_str = " ".join(cmd)
                        logging.info(f"Running command: {cmd_str}")
                        
                        # Run the command with shell=True to handle paths with spaces
                        result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
                        
                        if result.returncode != 0:
                            logging.error(f"Audio extraction failed for {video_path}")
                            logging.error(f"FFmpeg stderr: {result.stderr}")
                        else:
                            logging.info(f"Audio extraction successful for {video_path}")

                        audio_ready[index] = True
                    except Exception as e:
                        logging.error(f"Audio extraction exception for {video_path}: {e}")
                
                t = threading.Thread(target=extract_audio, args=(path, audio_path, ffmpeg_path, i))
                t.daemon = True
                t.start()
                audio_threads.append(t)
            else:
                # Create an empty file to avoid errors
                open(audio_path, 'w').close()
        else:
            scaled_img = load_and_scale_image(self, path, screen_width, screen_height)
            if scaled_img:
                scaled_images.append(scaled_img)
                gif_infos.append(None)
                media_types.append("image")
                video_paths.append(None)
                audio_files.append(None)
            else:
                scaled_images.append(None)
                gif_infos.append(None)
                media_types.append("image")
                video_paths.append(None)
                audio_files.append(None)

    # Filter valid media
    valid_indices = [i for i, media in enumerate(media_types) 
                   if media == "video" or (media == "image" and scaled_images[i]) or (media == "gif" and gif_infos[i])]
    if not valid_indices:
        logging.error("No valid media to display")
        print("No valid media to display")
        pygame.quit()
        return

    current_index = 0
    gif_frame_idx = 0
    gif_elapsed = 0
    clock = pygame.time.Clock()
    running = True
    
    # Video state
    video_cap = None
    video_start_time = 0
    video_paused = False
    last_video_frame = None
    last_video_pos = (0, 0)
    audio_playing = False

    while running:
        dt = clock.tick(60)
        actual_index = valid_indices[current_index]
        media_type = media_types[actual_index]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    # Find next valid media
                    next_index = current_index + 1
                    while next_index < len(valid_indices):
                        if valid_indices[next_index] != current_index:
                            break
                        next_index += 1
                    if next_index < len(valid_indices):
                        current_index = next_index
                        gif_frame_idx = 0
                        gif_elapsed = 0
                        video_paused = False
                        video_start_time = pygame.time.get_ticks()
                        last_video_frame = None
                        if audio_playing:
                            pygame.mixer.music.stop()
                            audio_playing = False
                        if video_cap:
                            video_cap.release()
                            video_cap = None
                elif event.key == pygame.K_LEFT:
                    # Find previous valid media
                    prev_index = current_index - 1
                    while prev_index >= 0:
                        if valid_indices[prev_index] != current_index:
                            break
                        prev_index -= 1
                    if prev_index >= 0:
                        current_index = prev_index
                        gif_frame_idx = 0
                        gif_elapsed = 0
                        video_paused = False
                        video_start_time = pygame.time.get_ticks()
                        last_video_frame = None
                        if audio_playing:
                            pygame.mixer.music.stop()
                            audio_playing = False
                        if video_cap:
                            video_cap.release()
                            video_cap = None
                elif event.key == pygame.K_f:
                    if screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
                    else:
                        pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                elif event.key == pygame.K_SPACE:
                    if media_types[valid_indices[current_index]] == "video":
                        video_paused = not video_paused
                        if video_paused:
                            if audio_playing:
                                pygame.mixer.music.pause()
                        else:
                            if audio_playing:
                                pygame.mixer.music.unpause()
                elif event.key == pygame.K_4:  # 5 seconds backward
                    if media_type == "video" and video_cap:
                        seek_video(video_cap, -5, video_fps, audio_playing, audio_ready[actual_index], video_paused)
                elif event.key == pygame.K_6:  # 5 seconds forward
                    if media_type == "video" and video_cap:
                        seek_video(video_cap, 5, video_fps, audio_playing, audio_ready[actual_index], video_paused)
                elif event.key == pygame.K_7:  # 10 seconds backward
                    if media_type == "video" and video_cap:
                        seek_video(video_cap, -10, video_fps, audio_playing, audio_ready[actual_index], video_paused)
                elif event.key == pygame.K_9:  # 10 seconds forward
                    if media_type == "video" and video_cap:
                        seek_video(video_cap, 10, video_fps, audio_playing, audio_ready[actual_index], video_paused)
                elif event.key == pygame.K_1:  # one frame backward
                    if media_type == "video" and video_cap:
                        step_frame(video_cap, -1, video_fps, audio_playing, audio_ready[actual_index], video_paused)
                elif event.key == pygame.K_3:  # one frame forward
                    if media_type == "video" and video_cap:
                        step_frame(video_cap, 1, video_fps, audio_playing, audio_ready[actual_index], video_paused)
        
        if media_type == "gif":
            frames, durations = gif_infos[actual_index]
            gif_elapsed += dt
            if gif_elapsed >= durations[gif_frame_idx]:
                gif_elapsed = 0
                gif_frame_idx = (gif_frame_idx + 1) % len(frames)
            current_image = frames[gif_frame_idx]
            screen.fill((0, 0, 0))
            img_width, img_height = current_image.get_size()
            x_pos = (screen_width - img_width) // 2
            y_pos = (screen_height - img_height) // 2
            screen.blit(current_image, (x_pos, y_pos))
            pygame.display.flip()
            
        elif media_type == "video":
            video_path = video_paths[actual_index]
            audio_path = audio_files[actual_index]
            
            if video_cap is None:
                logging.info(f"Opening video: {video_path}")
                video_cap = cv2.VideoCapture(video_path)
                if not video_cap.isOpened():
                    logging.error(f"Failed to open video: {video_path}")
                    # Move to next valid media
                    current_index = min(current_index + 1, len(valid_indices) - 1)
                    continue
                
                # Get video properties
                fps = video_cap.get(cv2.CAP_PROP_FPS)
                if fps <= 0:
                    fps = 30
                frame_delay = 1000 / fps
                
                # Try to load audio if available
                if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                    try:
                        logging.info(f"Loading audio: {audio_path}")
                        pygame.mixer.music.load(audio_path)
                        pygame.mixer.music.play()
                        audio_playing = True
                    except Exception as e:
                        logging.error(f"Failed to play audio: {e}")
                        audio_playing = False
                else:
                    logging.warning(f"No audio file found for {video_path}")
                    audio_playing = False
                
                video_start_time = pygame.time.get_ticks()
                
                video_fps = video_cap.get(cv2.CAP_PROP_FPS)
                if video_fps <= 0:
                    video_fps = 30
            
            if not video_paused:
                ret, frame = video_cap.read()
                if ret:
                    last_video_frame = surf
                    last_video_pos = (x_pos, y_pos)
                else:
                    # End of video, move to next
                    logging.info(f"End of video: {video_path}")
                    video_cap.release()
                    video_cap = None
                    if audio_playing:
                        pygame.mixer.music.stop()
                        audio_playing = False
                    current_index = min(current_index + 1, len(valid_indices) - 1)
                    continue
                    video_cap.set(cv2.CAP_PROP_POS_FRAMES, video_cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
                
                # Process and display frame
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, _ = frame.shape
                scale_factor = min(1.0, min(screen_width / w, screen_height / h))
                new_width = int(w * scale_factor)
                new_height = int(h * scale_factor)
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                
                # Convert to Pygame surface
                surf = pygame.surfarray.make_surface(frame)
                surf = pygame.transform.rotate(surf, -90)
                surf = pygame.transform.flip(surf, True, False)
                
                screen.fill((0, 0, 0))
                x_pos = (screen_width - new_width) // 2
                y_pos = (screen_height - new_height) // 2
                screen.blit(surf, (x_pos, y_pos))
                pygame.display.flip()
                
                # Save for pause state
                last_video_frame = surf
                last_video_pos = (x_pos, y_pos)
            else:
                # Show last frame when paused
                if last_video_frame:
                    screen.fill((0, 0, 0))
                    screen.blit(last_video_frame, last_video_pos)
                    pygame.display.flip()
                
        else:  # Static image
            current_image = scaled_images[actual_index]
            if current_image:
                screen.fill((0, 0, 0))
                img_width, img_height = current_image.get_size()
                x_pos = (screen_width - img_width) // 2
                y_pos = (screen_height - img_height) // 2
                screen.blit(current_image, (x_pos, y_pos))
                pygame.display.flip()

    # Clean up
    if video_cap:
        video_cap.release()
    if audio_playing:
        pygame.mixer.music.stop()
    pygame.quit()
    
    # Clean up audio files
    for audio_file in audio_files:
        if audio_file and os.path.exists(audio_file):
            try:
                os.unlink(audio_file)
            except Exception as e:
                logging.error(f"Error deleting audio file {audio_file}: {e}")
    
    logging.info("Media viewer closed")