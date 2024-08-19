import pygame
import sys
import numpy as np
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 10
BACKGROUND_COLOR = (0, 0, 0)  # White
ANT_COLOR = (255, 255, 255)  # Black
FOOD_COLOR = (255, 0, 0)  # Red


# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ant Pheromone Trail Simulation")

# Load the background image
background_image = pygame.image.load('gras.jpg') 
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) # Crop image size

# Pheromones of the Ants
# Constants
PHEROMONE_DECAY = 0.995 # PHEROMONE Decay in percent

# Initialize pheromone grid
pheromone_intensity_grid = np.zeros((SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE))

# Initialize pheromone surface with alpha
pheromone_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)

def draw_pheromones():
    for x in range(pheromone_intensity_grid.shape[0]):
        for y in range(pheromone_intensity_grid.shape[1]):
            intensity = pheromone_intensity_grid[x, y]
            if intensity > 0:
                # Create a PHEROMONE color with alpha based on intensity
                color = (255,179,67, int(255 * intensity)) # (255,179,67) is rpg color yellow/ochar
                pheromone_surface.fill(color)
                screen.blit(pheromone_surface, (x * GRID_SIZE, y * GRID_SIZE))

def global_pheromones_fading():
    global pheromone_intensity_grid
    # Fade pheromones by reducing intensity
    pheromone_intensity_grid *= PHEROMONE_DECAY  # Reduce by 5% per frame

#Ant Class
# Constants
PHEROMONE_SPREAD_INTENSITY = 0.5 # Strength of pheromone release
class Ant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.carrying_food = False
        self.angle = random.uniform(0, 360)  # Start with a random angle
        self.speed = 6  # Step size. The higher this number, the bigger circle, the better the angular resolution of movement. However, it also speeds up the movement.
        self.steps_since_last_change = 0  # Counter for steps
        self.steps_threshold = 3  # Update angle every "n" steps. This Controls the "speed" of the Ants.

    def move(self):
        
        # Increment the step counter
        self.steps_since_last_change += 1

        # Only update the angle every "n" steps
        if self.steps_since_last_change >= self.steps_threshold:
            angle_change = random.gauss(0, 10)  # Gaussian distribution for angle change
            self.angle += angle_change
            self.angle %= 360  # Keep angle within 0-360 degrees
            self.steps_since_last_change = 0  # Reset the counter

            # Convert angle to movement
            dx = self.speed * math.cos(math.radians(self.angle))
            dy = self.speed * math.sin(math.radians(self.angle))

            # Update position
            new_x = self.x + dx
            new_y = self.y + dy

            # Step off the boundaries and be reflected angle wise
            if new_x < 0 or new_x > SCREEN_WIDTH:
                dx = -dx
                self.angle = 180 - self.angle  # Reflect the angle

            if new_y < 0 or new_y > SCREEN_HEIGHT:
                dy = -dy
                self.angle = -self.angle % 360  # Reflect the angle; the % makes the angle lie within 0-365 degree

            # Update position with reflected direction
            self.x += dx
            self.y += dy

            # Keep within screen bounds (if desired, optional)
            self.x = max(0, min(self.x, SCREEN_WIDTH - 1))
            self.y = max(0, min(self.y, SCREEN_HEIGHT - 1))

    def release_pheremones(self):    # Update pheromone grid directly without bounds checking. Th min(1,...) ensures, that the Pheremones intensity does not exceed 1.
        grid_x = int(self.x // GRID_SIZE)
        grid_y = int(self.y // GRID_SIZE)
        pheromone_intensity_grid[grid_x, grid_y] = min(1, pheromone_intensity_grid[grid_x, grid_y] + PHEROMONE_SPREAD_INTENSITY)

    def draw(self):
        pygame.draw.circle(screen, ANT_COLOR, (int(self.x), int(self.y)), 5)

# Initializing a Clock - this sets the overall frame rate
clock = pygame.time.Clock()
# Main loop
running = True
ants = [Ant(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), Ant(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]  # List of ant objects, "//" is intager division
food_positions = []  # List of food positions

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                food_positions.append(event.pos)

    # Fill the background
    screen.fill(BACKGROUND_COLOR)
    # Draw the background image
    screen.blit(background_image, (0, 0))

    # Update pheromones (decay over time)
    global_pheromones_fading()

    # Draw pheromones
    draw_pheromones()

    # Move and draw ants and release their pheromones
    for ant in ants:
        ant.move()
        ant.draw()
        ant.release_pheremones()

    # Draw food
    for food in food_positions:
        pygame.draw.rect(screen, FOOD_COLOR, pygame.Rect(food[0] - 5, food[1] - 5, 10, 10))

    # Update display
    pygame.display.flip()
    # Cap the frame rate to 30 FPS
    clock.tick(30)