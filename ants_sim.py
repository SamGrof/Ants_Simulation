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
PHEROMONE_COLOR = (0, 0, 255)  # Blue
PHEROMONE_DECAY = 0.003  # Rate at which pheromones fade


# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ant Pheromone Trail Simulation")

# Load the background image
background_image = pygame.image.load('gras.jpg') 
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) # Crop image size

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

#Ant Class
# Constants
PHEROMONE_SPREAD_INTENSITY = 0.5 # Strength of pheromone release
class Ant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.carrying_food = False
        self.angle = random.uniform(0, 360)  # Start with a random angle
        self.speed = 4  # Step size or speed of movement
        self.steps_since_last_change = 0  # Counter for steps
        self.steps_threshold = 5  # Update angle every "n" steps

    def move(self):
        # Only update the angle every "n" steps
        if self.steps_since_last_change >= self.steps_threshold:
            angle_change = random.gauss(0, 10)  # Gaussian distribution for angle change
            self.angle += angle_change
            self.angle %= 360  # Keep angle within 0-360 degrees
            self.steps_since_last_change = 0  # Reset the counter

        # Increment the step counter
        self.steps_since_last_change += 1

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

        # Update pheromone grid
        grid_x = int(self.x // GRID_SIZE)
        grid_y = int(self.y // GRID_SIZE)
        if 0 <= grid_x < pheromone_grid.shape[0] and 0 <= grid_y < pheromone_grid.shape[1]:
            pheromone_grid[grid_x, grid_y] = min(1, pheromone_grid[grid_x, grid_y] + PHEROMONE_SPREAD_INTENSITY) 

    def draw(self):
        pygame.draw.circle(screen, ANT_COLOR, (int(self.x), int(self.y)), 5)

# Initializing a Clock - this sets the overall frame rate
clock = pygame.time.Clock()
# Main loop
running = True
ants = [Ant(SCREEN_WIDTH/2, SCREEN_HEIGHT/2), Ant(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)]  # List of ant objects
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
    # Cap the frame rate to 30 FPS
    clock.tick(30)