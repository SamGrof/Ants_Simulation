import pygame
import sys
import numpy as np
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
BACKGROUND_COLOR = (255, 255, 255)  # White
ANT_COLOR = (0, 0, 0)  # Black
FOOD_COLOR = (255, 0, 0)  # Red
PHEROMONE_COLOR = (0, 0, 255)  # Blue
PHEROMONE_DECAY = 0.0001  # Rate at which pheromones fade

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ant Pheromone Trail Simulation")

# Initialize pheromone grid
pheromone_grid = np.zeros((SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE))

def draw_pheromones():
    for x in range(pheromone_grid.shape[0]):
        for y in range(pheromone_grid.shape[1]):
            intensity = pheromone_grid[x, y]
            if intensity > 0:
                color = (0, 0, int(255 * intensity))
                pygame.draw.rect(screen, color, pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def update_pheromones():
    global pheromone_grid
    # Reduce pheromone intensity over time
    pheromone_grid = np.maximum(0, pheromone_grid - PHEROMONE_DECAY)

# Ant class
class Ant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.carrying_food = False

    def move(self):
        # Simple random walk
        self.x += random.choice([-1, 0, 1])
        self.y += random.choice([-1, 0, 1])
        # Keep within screen bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH - 1))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - 1))

        # Update pheromone grid (example)
        grid_x = self.x // GRID_SIZE
        grid_y = self.y // GRID_SIZE
        if 0 <= grid_x < pheromone_grid.shape[0] and 0 <= grid_y < pheromone_grid.shape[1]:
            pheromone_grid[grid_x, grid_y] = min(1, pheromone_grid[grid_x, grid_y] + 0.05)

    def draw(self):
        pygame.draw.circle(screen, ANT_COLOR, (self.x, self.y), 5)

# Main loop
running = True
ants = [Ant(100, 100), Ant(200, 200)]  # List of ant objects
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

    # Update pheromones (decay over time)
    update_pheromones()

    # Draw pheromones
    draw_pheromones()

    # Move and draw ants
    for ant in ants:
        ant.move()
        ant.draw()

    # Draw food
    for food in food_positions:
        pygame.draw.rect(screen, FOOD_COLOR, pygame.Rect(food[0] - 5, food[1] - 5, 10, 10))

    # Update display
    pygame.display.flip()