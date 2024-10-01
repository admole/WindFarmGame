import pygame
import sys
import matplotlib.pyplot as plt
import numpy as np
import math
from floris import FlorisModel
from floris.flow_visualization import visualize_cut_plane
import random

# Initialize pygame
pygame.init()

# Set up the window
WIDTH, HEIGHT = 2000, 1500
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Touch to add wind turbine to the wind farm')
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (200, 200, 255)
TEXT_COLOR = (0, 0, 0)

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
icon_size = (126, 126)
icon_image = pygame.transform.scale(icon_image, icon_size)
icon_image = pygame.transform.flip(icon_image, True, False)  # Horizontal flip

# Store icon positions
icon_positions = []
farm_powers = []

# Define minimum distance between icons
MIN_DISTANCE = 100  # Adjust this value as needed

font = pygame.font.Font(None, 90)


class WindParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(2, 5)
        self.speed = random.uniform(8.0, 10.0)
        self.direction = random.uniform(-0.5, 0.5)  # Slight variation in direction

    def update(self):
        # Move the particle in the wind direction
        self.x += self.speed
        self.y += self.direction

        # Reset the particle position if it moves off screen
        if self.x > WIDTH:
            self.x = 0
            self.y = random.randint(0, HEIGHT)

    def draw(self, surface):
        pygame.draw.circle(surface, BLUE, (int(self.x), int(self.y)), self.size)

def generate_plot(positions):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.axis('off')
    ax.set_position([0, 0, 1, 1])
    ax.set_xlim([0, WIDTH])
    ax.set_ylim([-HEIGHT, 0])
    farm_power = 0

    if len(positions) > 0:
        positions = np.array(positions)
        fli.set(layout_x=positions[:, 0], layout_y=-positions[:, 1])
        zero_yaws = np.zeros_like(positions[:, 0])
        fli.set(yaw_angles=zero_yaws[np.newaxis, :],
                wind_speeds=[8.0],
                wind_directions=[270.0],
                turbulence_intensities=[0.08])
        fli.run()
        horizontal_plane = fli.calculate_horizontal_plane(
            x_resolution=200,
            y_resolution=200,
            height=90.0,
        )

        # Plot the flow field with rotors
        visualize_cut_plane(horizontal_plane,
                            ax=ax,
                            label_contours=False,
                            cmap='Blues_r')

        farm_power = fli.get_farm_power()[0]

    # Save the plot as an image file
    plt.savefig('plot_background.png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()

    return farm_power


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


# setup floris
fli = FlorisModel('./gch.yaml')
_ = generate_plot(icon_positions)

# Create a list of particles
particles = [WindParticle() for _ in range(100)]

# Run the game loop
running = True
while running:
    window.fill(WHITE)
    # Load and display the updated plot image
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
    efficiency = farm_powers[-1]/(farm_powers[0]*len(farm_powers)+1e-12) if len(farm_powers) > 0 else 0.
    # Update and render the text showing the number of turbines
    turbine_count_text = font.render(f"Number of turbines: {len(icon_positions)}  Windfarm Efficiency: {efficiency*100:.1f}%", True, TEXT_COLOR)
    text_rect = turbine_count_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))  # Center text at the bottom of the screen
    window.blit(turbine_count_text, text_rect)

    # Update and draw each particle
    for particle in particles:
        particle.update()
        particle.draw(window)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button (or touch)
                mouse_x, mouse_y = event.pos

                # Check if the click is inside the rectangle
                if rect.collidepoint(mouse_x, mouse_y):
                    new_pos = (float(mouse_x), float(mouse_y))

                    # Check if the new position is too close to any existing icon
                    if not is_too_close(new_pos, icon_positions, MIN_DISTANCE):
                        icon_positions.append(new_pos)
                        new_power = generate_plot(icon_positions)
                        farm_powers.append(new_power)

                # Check if the click is inside the button
                if button_rect.collidepoint(mouse_x, mouse_y):
                    icon_positions.clear()  # Remove all icons
                    farm_powers.clear()
                    new_power = generate_plot(icon_positions)

        elif event.type == pygame.FINGERDOWN:
            # Convert normalized touch position to screen coordinates
            touch_x, touch_y = int(event.x * WIDTH), int(event.y * HEIGHT)

            # Check if the touch is inside the rectangle
            if rect.collidepoint(touch_x, touch_y):
                new_pos = (touch_x, touch_y)

                # Check if the new position is too close to any existing icon
                if not is_too_close(new_pos, icon_positions, MIN_DISTANCE):
                    icon_positions.append(new_pos)
                    new_power = generate_plot(icon_positions)
                    farm_powers.append(new_power)

            # Check if the touch is inside the button
            if button_rect.collidepoint(touch_x, touch_y):
                icon_positions.clear()  # Remove all icons
                farm_powers.clear()
                new_power = generate_plot(icon_positions)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Check if ESC key is pressed
                running = False

    # Update the display
    pygame.display.flip()
    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
