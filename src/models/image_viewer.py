import pygame
import os
import sys


def load_and_scale_image(self, image_path, screen_width, screen_height):
    try:
        self.imports_loaded.wait()
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


def show_images(image_paths):
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
    
    # Load and scale all images
    scaled_images = []
    for path in image_paths:
        scaled_img = load_and_scale_image(path, screen_width, screen_height)
        if scaled_img:
            scaled_images.append(scaled_img)
    
    if not scaled_images:
        print("No valid images to display.")
        pygame.quit()
        sys.exit(1)
    
    current_index = 0
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RIGHT:
                    current_index = (current_index + 1) % len(scaled_images)
                elif event.key == pygame.K_LEFT:
                    current_index = (current_index - 1) % len(scaled_images)
                elif event.key == pygame.K_f:  # Toggle true fullscreen with F key
                    if screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
                    else:
                        pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        
        # Clear screen with black
        screen.fill((0, 0, 0))
        
        # Display current image centered
        current_image = scaled_images[current_index]
        img_width, img_height = current_image.get_size()
        x_pos = (screen_width - img_width) // 2
        y_pos = (screen_height - img_height) // 2
        screen.blit(current_image, (x_pos, y_pos))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()