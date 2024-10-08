import numpy as np
import sys
# sys.path.append('./floris')
# from floris import FlorisModel
import asyncio
import math
import random
import pygame


FPS = 30
WIDTH, HEIGHT = 2000, 1500

# Define colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (200, 200, 255)
TEXT_COLOR = (0, 0, 0)

MIN_DISTANCE = 100  # Adjust this value as needed


class WindParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(2, 5)
        self.speed = random.uniform(8.0, 10.0)
        self.direction = random.uniform(-0.5, 0.5)  # Slight variation in direction

    def update(self, positions):
        for turbine_pos in positions:
            if abs(self.y - turbine_pos[1]) < 126:
                if self.x > turbine_pos[0]:
                    self.speed = random.uniform(4.0, 5.0)

        # Move the particle in the wind direction
        self.x += self.speed
        self.y += self.direction

        # Reset the particle position if it moves off screen
        if self.x > WIDTH:
            self.x = 0
            self.y = random.randint(0, HEIGHT)
            self.speed = random.uniform(8.0, 10.0)

    def draw(self, surface):
        pygame.draw.circle(surface, BLUE, (int(self.x), int(self.y)), self.size)


# def get_power(positions, fli):
#     farm_power = 0
#
#     if len(positions) > 0:
#         positions = np.array(positions)
#         fli.set(layout_x=positions[:, 0], layout_y=-positions[:, 1])
#         zero_yaws = np.zeros_like(positions[:, 0])
#         fli.set(yaw_angles=zero_yaws[np.newaxis, :],
#                 wind_speeds=[8.0],
#                 wind_directions=[270.0],
#                 turbulence_intensities=[0.08])
#         fli.run()
#         farm_power = fli.get_farm_power()[0]
#
#     return farm_power

def get_power(positions, fli):
    return len(positions) + 1


def is_too_close(new_pos, existing_positions, min_distance):
    """Check if the new position is too close to any existing positions."""
    for pos in existing_positions:
        distance = math.hypot(new_pos[0] - pos[0], new_pos[1] - pos[1])
        if distance < min_distance:
            return True
    return False


def draw_button(window):
    """Draw the button and its text on the screen."""
    # Define the button
    button_width, button_height = 175, 50
    button_x, button_y = WIDTH - button_width - 20, HEIGHT - button_height - 20
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    button_color = RED
    button_text = 'Clear Turbines'
    pygame.draw.rect(window, button_color, button_rect)
    font = pygame.font.Font(None, 36)
    text_surface = font.render(button_text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    window.blit(text_surface, text_rect)
    return button_rect


# Game loop
async def main():
    # Initialize pygame
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Touch to add wind turbine to the wind farm')
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 90)

    # Define the rectangular area
    rect_x, rect_y = 100, 100
    rect_width, rect_height = 1800, 1300
    rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)


    # Load the icon image (Ensure it's in the correct path accessible in the browser)
    icon_image = pygame.image.load('./assets/icon.png')

    # Resize the icon image if necessary
    icon_size = (126, 126)
    icon_image = pygame.transform.scale(icon_image, icon_size)
    icon_image = pygame.transform.flip(icon_image, True, False)  # Horizontal flip

    # Store icon positions
    icon_positions = []
    farm_powers = []


    # setup floris
    # fli = FlorisModel('./assets/models/gch.yaml')
    # fli = 1

    pygame.display.update()

    # Create a list of particles
    particles = [WindParticle() for _ in range(5000)]

    running = True
    while running:
        screen.fill(WHITE)

        pygame.draw.rect(screen, GRAY, rect, 5)

        for pos in icon_positions:
            screen.blit(icon_image, (pos[0] - icon_size[0] // 2, pos[1] - icon_size[1] // 2))

        button = draw_button(screen)
        efficiency = farm_powers[-1]/(farm_powers[0]*len(farm_powers)+1e-12) if len(farm_powers) > 0 else 0.
        turbine_count_text = font.render(f"Number of turbines: {len(icon_positions)}  Windfarm Efficiency: {efficiency*100:.1f}%", True, TEXT_COLOR)
        text_rect = turbine_count_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        screen.blit(turbine_count_text, text_rect)

        for particle in particles:
            particle.update(icon_positions)
            particle.draw(screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if rect.collidepoint(mouse_x, mouse_y):
                        new_pos = (float(mouse_x), float(mouse_y))
                        if not is_too_close(new_pos, icon_positions, MIN_DISTANCE):
                            icon_positions.append(new_pos)
                            # new_power = get_power(icon_positions, fli)
                            # farm_powers.append(new_power)

                    if button.collidepoint(mouse_x, mouse_y):
                        icon_positions.clear()
                        # farm_powers.clear()
                        # new_power = get_power(icon_positions)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)


if __name__ == '__main__':
    asyncio.run(main())
