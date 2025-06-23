import pygame
import os
import sys
from PIL import Image  # Add Pillow for GIF support
import cv2  # For mp4 playback


def load_and_scale_image(self, image_path, screen_width, screen_height):
    try:
        self.imports_loaded.wait()
        image = pygame.image.load(image_path)
        # Ensure image is 24-bit or 32-bit for smooth scaling
        if image.get_alpha() is not None:
            image = image.convert_alpha()
        else:
            image = image.convert()
        image_width, image_height = image.get_size()
        
        # Calculate scaling factor to fit the screen while maintaining aspect ratio
        # Only scale down, never scale up
        scale_factor = min(
            1.0,
            min(screen_width / image_width, screen_height / image_height)
        )
        new_width = int(image_width * scale_factor)
        new_height = int(image_height * scale_factor)
        
        # Scale the image only if needed
        if scale_factor < 1.0:
            scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
        else:
            scaled_image = image
        return scaled_image
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


def load_gif_frames(image_path, screen_width, screen_height):
    """Load all frames from a GIF and scale them to fit the screen."""
    frames = []
    durations = []
    try:
        img = Image.open(image_path)
        # Get duration for each frame (in ms)
        while True:
            frame = img.convert("RGBA")
            # Scale frame to fit screen
            img_width, img_height = frame.size
            scale_factor = min(
                1.0,
                min(screen_width / img_width, screen_height / img_height)
            )
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            frame = frame.resize((new_width, new_height), Image.LANCZOS)
            # Convert to pygame surface
            mode = frame.mode
            data = frame.tobytes()
            surface = pygame.image.fromstring(data, frame.size, mode)
            frames.append(surface)
            durations.append(img.info.get('duration', 100))  # default 100ms
            img.seek(img.tell() + 1)
    except EOFError:
        pass  # End of sequence
    except Exception as e:
        print(f"Error loading GIF {image_path}: {e}")
    return frames, durations


def show_images(self, image_paths):
    # Initialize Pygame
    pygame.init()
    
    # Get the screen info
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    
    # Create a borderless window at position (0,0) covering the entire screen
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Image Viewer")
    
    # Position window at top-left corner
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    
    # Load and scale all images (support GIFs and mark mp4s)
    scaled_images = []
    gif_infos = []  # List of (frames, durations) or None for static images
    media_types = []  # "image", "gif", or "mp4"
    video_paths = []
    for path in image_paths:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".gif":
            frames, durations = load_gif_frames(path, screen_width, screen_height)
            if frames:
                scaled_images.append(frames[0])
                gif_infos.append((frames, durations))
                media_types.append("gif")
                video_paths.append(None)
            else:
                gif_infos.append(None)
                media_types.append("image")
                video_paths.append(None)
        elif ext == ".mp4":
            scaled_images.append(None)
            gif_infos.append(None)
            media_types.append("mp4")
            video_paths.append(path)
        else:
            scaled_img = load_and_scale_image(self, path, screen_width, screen_height)
            if scaled_img:
                scaled_images.append(scaled_img)
                gif_infos.append(None)
                media_types.append("image")
                video_paths.append(None)

    if not scaled_images:
        print("No valid images to display.")
        pygame.quit()
        return

    current_index = 0
    gif_frame_idx = 0
    gif_elapsed = 0

    clock = pygame.time.Clock()
    running = True

    video_cap = None
    video_fps = 30
    video_frame_time = 0
    video_last_frame = 0
    video_paused = False

    while running:
        dt = clock.tick(60)  # milliseconds since last tick
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    if current_index < len(scaled_images) - 1:
                        current_index += 1
                        gif_frame_idx = 0
                        gif_elapsed = 0
                        # Release video if switching away
                        if video_cap is not None:
                            video_cap.release()
                            video_cap = None
                elif event.key == pygame.K_LEFT:
                    if current_index > 0:
                        current_index -= 1
                        gif_frame_idx = 0
                        gif_elapsed = 0
                        if video_cap is not None:
                            video_cap.release()
                            video_cap = None
                elif event.key == pygame.K_f:
                    if screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
                    else:
                        pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                elif event.key == pygame.K_SPACE:
                    if media_types[current_index] == "mp4":
                        video_paused = not video_paused

        media_type = media_types[current_index]
        if media_type == "gif":
            # Handle GIF animation
            frames, durations = gif_infos[current_index]
            gif_elapsed += dt
            if gif_elapsed >= durations[gif_frame_idx]:
                gif_elapsed = 0
                gif_frame_idx = (gif_frame_idx + 1) % len(frames)
            current_image = frames[gif_frame_idx]
            # Draw GIF frame
            screen.fill((0, 0, 0))
            img_width, img_height = current_image.get_size()
            x_pos = (screen_width - img_width) // 2
            y_pos = (screen_height - img_height) // 2
            screen.blit(current_image, (x_pos, y_pos))
            pygame.display.flip()
        elif media_type == "mp4":
            if video_cap is None:
                video_cap = cv2.VideoCapture(video_paths[current_index])
                if not video_cap.isOpened():
                    print(f"Failed to open video: {video_paths[current_index]}")
                    current_index += 1
                    if video_cap is not None:
                        video_cap.release()
                        video_cap = None
                    continue
                video_fps = video_cap.get(cv2.CAP_PROP_FPS) or 30
                video_frame_time = 1000 / video_fps
                video_next_frame_time = pygame.time.get_ticks()
                video_paused = False

            if not video_paused:
                now = pygame.time.get_ticks()
                # Only process if it's time for the next frame
                if now >= video_next_frame_time:
                    # Calculate how many frames we need to advance
                    frames_to_advance = 1
                    # If we're behind, skip frames to catch up
                    if now > video_next_frame_time + video_frame_time:
                        frames_to_advance = min(
                            10,  # Limit to 10 frames max to avoid large jumps
                            int((now - video_next_frame_time) / video_frame_time)
                        )
                    
                    # Skip frames if needed
                    for _ in range(frames_to_advance - 1):
                        if not video_cap.grab():
                            break
                    
                    # Read the current frame
                    ret, frame = video_cap.read()
                    if not ret:
                        # End of video handling
                        video_cap.release()
                        video_cap = None
                        current_index += 1
                        if current_index >= len(scaled_images):
                            running = False
                        continue
                    
                    # Update timing for next frame
                    video_next_frame_time += frames_to_advance * video_frame_time
                    
                    # Process and display frame
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, _ = frame.shape
                    scale_factor = min(1.0, min(screen_width / w, screen_height / h))
                    new_width = int(w * scale_factor)
                    new_height = int(h * scale_factor)
                    frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                    surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    
                    screen.fill((0, 0, 0))
                    x_pos = (screen_width - new_width) // 2
                    y_pos = (screen_height - new_height) // 2
                    screen.blit(surf, (x_pos, y_pos))
                    pygame.display.flip()
        else:
            # Static image
            current_image = scaled_images[current_index]
            screen.fill((0, 0, 0))
            img_width, img_height = current_image.get_size()
            x_pos = (screen_width - img_width) // 2
            y_pos = (screen_height - img_height) // 2
            screen.blit(current_image, (x_pos, y_pos))
            pygame.display.flip()

    if video_cap is not None:
        video_cap.release()
    pygame.quit()
    return