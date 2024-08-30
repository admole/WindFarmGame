import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Set up the window
WIDTH, HEIGHT = 2000, 1500
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Touch to Place Icon')

# Define colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Define the rectangular area
rect_x, rect_y = 100, 100
rect_width, rect_height = 1800, 1300
rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)

# Load the icon image
icon_image = pygame.image.load('icon.png')

# Resize the icon image if necessary
icon_size = (100, 100)
icon_image = pygame.transform.scale(icon_image, icon_size)

# Create mirrored versions of the icon
icon_image = pygame.transform.flip(icon_image, True, False)  # Horizontal flip

# Store icon positions
icon_positions = []

# Define minimum distance between icons
MIN_DISTANCE = 100  # Adjust this value as needed

def is_too_close(new_pos, existing_positions, min_distance):
    """Check if the new position is too close to any existing positions."""
    for pos in existing_positions:
        distance = math.hypot(new_pos[0] - pos[0], new_pos[1] - pos[1])
        if distance < min_distance:
            return True
    return False

# Run the game loop
running = True
while running:
    window.fill(WHITE)

    # Draw the rectangle
    pygame.draw.rect(window, GRAY, rect)

    # Draw all icons
    for i, pos in enumerate(icon_positions):
        window.blit(icon_image, (pos[0] - icon_size[0] // 2, pos[1] - icon_size[1] // 2))

    # Todo: add floris interface here

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button (or touch)
                # Get mouse position
                mouse_x, mouse_y = event.pos

                # Check if the click is inside the rectangle
                if rect.collidepoint(mouse_x, mouse_y):
                    new_pos = (mouse_x, mouse_y)

                    # Check if the new position is too close to any existing icon
                    if not is_too_close(new_pos, icon_positions, MIN_DISTANCE):
                        # Save the position of the icon
                        icon_positions.append(new_pos)

        elif event.type == pygame.FINGERDOWN:
            # Convert normalized touch position to screen coordinates
            touch_x, touch_y = int(event.x * WIDTH), int(event.y * HEIGHT)

            # Check if the touch is inside the rectangle
            if rect.collidepoint(touch_x, touch_y):
                new_pos = (touch_x, touch_y)

                # Check if the new position is too close to any existing icon
                if not is_too_close(new_pos, icon_positions, MIN_DISTANCE):
                    # Save the position of the icon
                    icon_positions.append(new_pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Check if ESC key is pressed
                running = False

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
