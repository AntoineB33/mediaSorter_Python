import pygame
import os
import sys
from PIL import Image  # Add Pillow for GIF support


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
    
    # Load and scale all images (support GIFs)
    scaled_images = []
    gif_infos = []  # List of (frames, durations) or None for static images
    for path in image_paths:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".gif":
            frames, durations = load_gif_frames(path, screen_width, screen_height)
            if frames:
                scaled_images.append(frames[0])
                gif_infos.append((frames, durations))
            else:
                gif_infos.append(None)
        else:
            scaled_img = load_and_scale_image(self, path, screen_width, screen_height)
            if scaled_img:
                scaled_images.append(scaled_img)
                gif_infos.append(None)

    if not scaled_images:
        print("No valid images to display.")
        pygame.quit()
        return

    current_index = 0
    gif_frame_idx = 0
    gif_elapsed = 0

    clock = pygame.time.Clock()
    running = True
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
                elif event.key == pygame.K_LEFT:
                    if current_index > 0:
                        current_index -= 1
                        gif_frame_idx = 0
                        gif_elapsed = 0
                elif event.key == pygame.K_f:
                    if screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
                    else:
                        pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

        # Handle GIF animation
        gif_info = gif_infos[current_index]
        if gif_info:
            frames, durations = gif_info
            gif_elapsed += dt
            if gif_elapsed >= durations[gif_frame_idx]:
                gif_elapsed = 0
                gif_frame_idx = (gif_frame_idx + 1) % len(frames)
            current_image = frames[gif_frame_idx]
        else:
            current_image = scaled_images[current_index]

        # Clear screen and display image centered
        screen.fill((0, 0, 0))
        img_width, img_height = current_image.get_size()
        x_pos = (screen_width - img_width) // 2
        y_pos = (screen_height - img_height) // 2
        screen.blit(current_image, (x_pos, y_pos))
        pygame.display.flip()

    pygame.quit()
    return