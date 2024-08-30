import pygame
import sys
import matplotlib.pyplot as plt
import numpy as np
import math

# Initialize pygame
pygame.init()

# Set up the window
WIDTH, HEIGHT = 2000, 1500
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Touch to add wind turbine to the wind farm')

# Define colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Define the rectangular area
rect_x, rect_y = 100, 100
rect_width, rect_height = 1800, 1300
rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)

# Define the button
button_width, button_height = 175, 50
button_x, button_y = WIDTH - button_width - 20, HEIGHT - button_height - 20
button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
button_color = RED
button_text = 'Clear Turbines'

# Load the icon image
icon_image = pygame.image.load('icon.png')

# Resize the icon image if necessary
icon_size = (100, 100)
icon_image = pygame.transform.scale(icon_image, icon_size)
icon_image = pygame.transform.flip(icon_image, True, False)  # Horizontal flip

# Store icon positions
icon_positions = []

# Define minimum distance between icons
MIN_DISTANCE = 100  # Adjust this value as needed


def generate_plot(positions):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.axis('off')
    ax.set_position([0, 0, 1, 1])
    ax.set_xlim([0, WIDTH])
    ax.set_ylim([-HEIGHT, 0])

    if len(positions) > 0:
        positions = np.array(positions)
        plt.scatter(positions[:, 0], -positions[:, 1])

    # Save the plot as an image file
    plt.savefig('plot_background.png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()


def is_too_close(new_pos, existing_positions, min_distance):
    """Check if the new position is too close to any existing positions."""
    for pos in existing_positions:
        distance = math.hypot(new_pos[0] - pos[0], new_pos[1] - pos[1])
        if distance < min_distance:
            return True
    return False


def draw_button():
    """Draw the button and its text on the screen."""
    pygame.draw.rect(window, button_color, button_rect)
    font = pygame.font.Font(None, 36)
    text_surface = font.render(button_text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    window.blit(text_surface, text_rect)


# Run the game loop
running = True
while running:
    window.fill(WHITE)
    # Load and display the updated plot image
    generate_plot(icon_positions)
    plot_image = pygame.image.load('plot_background.png')  # Reload updated plot
    plot_image = pygame.transform.scale(plot_image, (WIDTH, HEIGHT))
    window.blit(plot_image, (0, 0))  # Draw the plot image as the background

    # Draw the rectangle
    pygame.draw.rect(window, GRAY, rect, 5)

    # Draw all icons
    for pos in icon_positions:
        window.blit(icon_image, (pos[0] - icon_size[0] // 2, pos[1] - icon_size[1] // 2))

    # Draw the button
    draw_button()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button (or touch)
                mouse_x, mouse_y = event.pos

                # Check if the click is inside the rectangle
                if rect.collidepoint(mouse_x, mouse_y):
                    new_pos = (mouse_x, mouse_y)
                    print(new_pos)

                    # Check if the new position is too close to any existing icon
                    if not is_too_close(new_pos, icon_positions, MIN_DISTANCE):
                        icon_positions.append(new_pos)

                # Check if the click is inside the button
                if button_rect.collidepoint(mouse_x, mouse_y):
                    icon_positions.clear()  # Remove all icons

        elif event.type == pygame.FINGERDOWN:
            # Convert normalized touch position to screen coordinates
            touch_x, touch_y = int(event.x * WIDTH), int(event.y * HEIGHT)

            # Check if the touch is inside the rectangle
            if rect.collidepoint(touch_x, touch_y):
                new_pos = (touch_x, touch_y)

                # Check if the new position is too close to any existing icon
                if not is_too_close(new_pos, icon_positions, MIN_DISTANCE):
                    icon_positions.append(new_pos)

            # Check if the touch is inside the button
            if button_rect.collidepoint(touch_x, touch_y):
                icon_positions.clear()  # Remove all icons

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Check if ESC key is pressed
                running = False

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
