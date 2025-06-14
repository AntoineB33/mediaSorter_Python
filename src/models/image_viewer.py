import pygame
import os
import sys


def load_and_scale_image(image_path, screen_width, screen_height):
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
    # Implementation here
    pass