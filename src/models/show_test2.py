import pygame
import sys
import os
import cv2
import numpy as np

# Initialize pygame mixer for audio
pygame.mixer.init()

def load_and_scale_image(image_path, screen_width, screen_height):
    try:
        image = pygame.image.load(image_path)
        image_width, image_height = image.get_size()
        
        # Calculate scaling factor to fit the screen while maintaining aspect ratio
        scale_factor = min(screen_width / image_width, screen_height / image_height)
        new_width = int(image_width * scale_factor)
        new_height = int(image_height * scale_factor)
        
        # Scale the image
        scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
        return scaled_image
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

def load_video(video_path, screen_width, screen_height):
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error opening video {video_path}")
            return None
            
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate scaling factor
        scale_factor = min(screen_width / width, screen_height / height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        return {
            'cap': cap,
            'width': width,
            'height': height,
            'fps': fps,
            'frame_count': frame_count,
            'target_width': new_width,
            'target_height': new_height,
            'paused': False,
            'position': 0
        }
    except Exception as e:
        print(f"Error loading video {video_path}: {e}")
        return None

def main(media_paths):
    # Initialize Pygame
    pygame.init()
    
    # Get the screen info
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    
    # Create a borderless window
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Media Viewer")
    
    # Position window at top-left corner
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    
    # Load media
    media_list = []
    for path in media_paths:
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            img = load_and_scale_image(path, screen_width, screen_height)
            if img:
                media_list.append({
                    'type': 'image',
                    'path': path,
                    'data': img
                })
        elif ext in ['.mp4', '.mkv', '.avi', '.mov', '.mpg', '.mpeg']:
            vid = load_video(path, screen_width, screen_height)
            if vid:
                media_list.append({
                    'type': 'video',
                    'path': path,
                    'data': vid
                })
    
    if not media_list:
        print("No valid media to display.")
        pygame.quit()
        sys.exit(1)
    
    current_index = 0
    clock = pygame.time.Clock()
    last_time = pygame.time.get_ticks()
    
    # Main loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0  # Convert to seconds
        last_time = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    # Release current video if playing
                    if media_list[current_index]['type'] == 'video':
                        media_list[current_index]['data']['cap'].release()
                    current_index = min(current_index + 1, len(media_list))
                elif event.key == pygame.K_LEFT:
                    # Release current video if playing
                    if media_list[current_index]['type'] == 'video':
                        media_list[current_index]['data']['cap'].release()
                    current_index = max(current_index - 1, 0)
                elif event.key == pygame.K_f:  # Toggle fullscreen
                    if screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
                    else:
                        pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                elif event.key in [pygame.K_SPACE, pygame.K_k]:  # Pause/Play with space or k
                    if media_list[current_index]['type'] == 'video':
                        media_list[current_index]['data']['paused'] = not media_list[current_index]['data']['paused']
                elif event.key == pygame.K_6:  # Move forward 5 seconds
                    if media_list[current_index]['type'] == 'video':
                        vid = media_list[current_index]['data']['data']
                        current_frame = vid['cap'].get(cv2.CAP_PROP_POS_FRAMES)
                        new_frame = min(vid['frame_count'] - 1, current_frame + 5 * vid['fps'])
                        vid['cap'].set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                        vid['position'] = new_frame
                elif event.key == pygame.K_4:  # Move backward 5 seconds
                    if media_list[current_index]['type'] == 'video':
                        vid = media_list[current_index]['data']['data']
                        current_frame = vid['cap'].get(cv2.CAP_PROP_POS_FRAMES)
                        new_frame = max(0, current_frame - 5 * vid['fps'])
                        vid['cap'].set(cv2.CAP_PROP_POS_FRAMES, new_frame)
                        vid['position'] = new_frame
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Handle current media
        current_media = media_list[current_index]
        if current_media['type'] == 'image':
            img = current_media['data']
            img_width, img_height = img.get_size()
            x_pos = (screen_width - img_width) // 2
            y_pos = (screen_height - img_height) // 2
            screen.blit(img, (x_pos, y_pos))
            
            # Display media type indicator
            font = pygame.font.SysFont(None, 36)
            text = font.render("Image", True, (255, 255, 255))
            screen.blit(text, (20, 20))
            
        elif current_media['type'] == 'video':
            video = current_media['data']
            cap = video['cap']
            
            # Read next frame if not paused
            if not video['paused']:
                ret, frame = cap.read()
                if ret:
                    # Convert frame to RGB and pygame surface
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = np.rot90(frame)  # Rotate because pygame surface is different orientation
                    frame = pygame.surfarray.make_surface(frame)
                    
                    # Scale to fit screen
                    scaled_frame = pygame.transform.smoothscale(frame, 
                                                              (video['target_width'], 
                                                               video['target_height']))
                    
                    # Center on screen
                    x_pos = (screen_width - video['target_width']) // 2
                    y_pos = (screen_height - video['target_height']) // 2
                    screen.blit(scaled_frame, (x_pos, y_pos))
                    
                    # Update video position
                    video['position'] = cap.get(cv2.CAP_PROP_POS_FRAMES)
                else:
                    # End of video - restart
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # Display video controls
            font = pygame.font.SysFont(None, 36)
            status = "PAUSED" if video['paused'] else "PLAYING"
            text = font.render(f"Video: {status}", True, (255, 255, 255))
            screen.blit(text, (20, 20))
            
            # Progress bar
            if video['frame_count'] > 0:
                progress = video['position'] / video['frame_count']
                bar_width = screen_width - 40
                pygame.draw.rect(screen, (100, 100, 100), (20, 70, bar_width, 20))
                pygame.draw.rect(screen, (0, 255, 0), (20, 70, int(bar_width * progress), 20))
        
        # Display navigation info
        font = pygame.font.SysFont(None, 36)
        info = font.render(f"{current_index+1}/{len(media_list)}", True, (255, 255, 255))
        screen.blit(info, (screen_width - info.get_width() - 20, 20))
        
        # Display help
        help_font = pygame.font.SysFont(None, 24)
        help_text = help_font.render("← →: Navigate  K: Play/Pause  4/6: Seek ±5s  F: Fullscreen  ESC: Quit", True, (200, 200, 200))
        screen.blit(help_text, (screen_width // 2 - help_text.get_width() // 2, screen_height - 40))
        
        pygame.display.flip()
        clock.tick(30)  # Cap at 30 FPS
    
    # Release all video resources
    for media in media_list:
        if media['type'] == 'video':
            media['data']['cap'].release()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Example list of media paths
    media_paths = [
        "data/media/image1.jpg",
        "data/media/video1.mkv",
        "data/media/image2.jpg",
        "data/media/video2.mkv"
    ]
    
    # Ensure paths are absolute or correctly relative
    media_paths = [os.path.abspath(path) for path in media_paths]
    
    main(media_paths)