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
GRID_SIZE = 5
BACKGROUND_COLOR = (0, 0, 0)  # Black
ANT_COLOR = (255, 255, 255)  # White
FOOD_COLOR = (255, 0, 0)  # Red
FRAMES_PER_SECOND = 30 # How many frames per second are updated; used in pygame.time.Clock()


# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ant Pheromone Trail Simulation")

# Load the background image
background_image = pygame.image.load('gras.jpg') 
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)) # Crop image size

# Food Field & Food Sources


SMELL_STRENGHT = 80  # The strength of the emitting food field
FOOD_SMELL_RADIUS = 50  # Cutoff radius for the smell field
GLOBAL_FOOD_FIELD_REDUCTION = 0.005  # Reduction per frame for the global smell field
LOCAL_FOOD_FIELD_UPDATE = 200  # Number of cycles before updating each food source's smell field

# Load the mushroom image
mushroom_image = pygame.image.load('mushroom1.png')

# Define the target size for the cropped image
target_size = (32, 32)  # Width, Height

# Scale down the image to the target size
cropped_mushroom_image = pygame.transform.scale(mushroom_image, target_size)

class FoodSource:
    def __init__(self, x, y):
        self.position = (x, y)
        self.grid_radius = FOOD_SMELL_RADIUS // GRID_SIZE
        self.update_cycle = 0  # Track update cycles

    def update_smell(self, smell_grid):
        food_x, food_y = self.position
        food_grid_x = food_x // GRID_SIZE
        food_grid_y = food_y // GRID_SIZE

        for x in range(food_grid_x - self.grid_radius, food_grid_x + self.grid_radius + 1):
            for y in range(food_grid_y - self.grid_radius, food_grid_y + self.grid_radius + 1):
                if 0 <= x < smell_grid.shape[0] and 0 <= y < smell_grid.shape[1]:
                    dx = (x * GRID_SIZE + GRID_SIZE // 2) - food_x
                    dy = (y * GRID_SIZE + GRID_SIZE // 2) - food_y
                    distance_squared = dx**2 + dy**2
                    if distance_squared > 0 and distance_squared <= FOOD_SMELL_RADIUS**2:
                        intensity = min(1, SMELL_STRENGHT / distance_squared)
                        smell_grid[x, y] = max(smell_grid[x, y], intensity)

    def draw(self, screen):
        x_position = self.position[0] - cropped_mushroom_image.get_width() // 2
        y_position = self.position[1] - cropped_mushroom_image.get_height()
        screen.blit(cropped_mushroom_image, (x_position, y_position))

class FoodField:
    def __init__(self, screen_width, screen_height, grid_size):
        self.food_sources = []
        self.smell_grid = np.zeros((screen_width // grid_size, screen_height // grid_size))

    def add_food_source(self, position):
        new_food = FoodSource(position[0], position[1])
        self.food_sources.append(new_food)

    def remove_food_source(self, food_source):
        if food_source in self.food_sources:
            self.food_sources.remove(food_source)

    def update(self):
        # Apply global reduction
        self.smell_grid -= GLOBAL_FOOD_FIELD_REDUCTION
        self.smell_grid = np.clip(self.smell_grid, 0, 1)  # Ensure values stay between 0 and 1

        # Update smell for each food source on its own cycle
        for food_source in self.food_sources:
            food_source.update_cycle += 1
            if food_source.update_cycle >= LOCAL_FOOD_FIELD_UPDATE:
                food_source.update_smell(self.smell_grid)
                food_source.update_cycle = 0

    def draw(self, screen):
        # Draw the smell field
        for x in range(self.smell_grid.shape[0]):
            for y in range(self.smell_grid.shape[1]):
                intensity = self.smell_grid[x, y]
                if intensity > 0:  # Only draw if intensity is greater than 0
                    color = (252, 89, 163, int(255 * intensity))  # Set color with alpha
                    temp_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                    temp_surface.fill(color)
                    screen.blit(temp_surface, (x * GRID_SIZE, y * GRID_SIZE))

        # Draw each food source
        for food_source in self.food_sources:
            food_source.draw(screen)



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


# Ant Stack
# Load the ant stack image
ant_stack_image = pygame.image.load('ant_hole_pixel.png')

# Scale down the image to the target size
target_size_stack = (64, 64)  # Width, Height
cropped_ant_stack_image = pygame.transform.scale(ant_stack_image, target_size_stack)

# Define the ant stack position (centered)
ant_stack_position = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)  # Adjust as needed


#Ant Class
# Constants
PHEROMONE_SPREAD_INTENSITY = 0.5 # Strength of pheromone release
class Ant:
    def __init__(self, x, y,smell_grid):
        self.x = x
        self.y = y
        self.carrying_food = False
        self.angle = random.uniform(0, 360)  # Start with a random angle
        self.speed = 3  # Step size. The higher this number, the bigger circle, the better the angular resolution of movement. However, it also speeds up the movement.
        self.steps_since_last_change = 0  # Counter for steps
        self.steps_threshold = 3  # Update angle every "n" steps. This Controls the "speed" of the Ants.
        self.smell_grid = smell_grid  # Reference to the smell gri

  # Load and scale the ant image
        self.image = pygame.image.load('ant1.png')
        self.image = pygame.transform.scale(self.image, (30, 30))  # Scale to desired size
        
        self.rect = self.image.get_rect(center=(self.x, self.y))



    def move(self):
        
        # Increment the step counter
        self.steps_since_last_change += 1


        # Grid position of the ant
        grid_x = int(self.x // GRID_SIZE)
        grid_y = int(self.y // GRID_SIZE)

        # Define possible movement directions (dx, dy) relative to the grid
        directions = [(-1, -1), (0, -1), (1, -1), 
                      (-1, 0),  (0, 0),  (1, 0), 
                      (-1, 1),  (0, 1),  (1, 1)]
        
        best_direction = (0, 0)
        highest_intensity = 0  

        # Check surrounding cells for food smell
        for dx, dy in directions:
            new_x, new_y = grid_x + dx, grid_y + dy
            if 0 <= new_x < self.smell_grid.shape[0] and 0 <= new_y < self.smell_grid.shape[1]:
                intensity = self.smell_grid[new_x, new_y]
                if intensity > highest_intensity:
                    highest_intensity = intensity
                    best_direction = (dx, dy)

        # If a strong smell is detected, move towards it
        if highest_intensity > 0:
            # Calculate the new direction
            dx = round(best_direction[0] * self.speed)
            dy = round(best_direction[1] * self.speed)

            # Update the angle based on the direction
            self.angle = math.degrees(math.atan2(dy, dx))
        else:
            # Smoothed Random Walk. Only update the angle every "n" steps
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
        # Update the rect position (used for image) to the new position
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def release_pheremones(self):    # Update pheromone grid directly without bounds checking. Th min(1,...) ensures, that the Pheremones intensity does not exceed 1.
        grid_x = int(self.x // GRID_SIZE)
        grid_y = int(self.y // GRID_SIZE)
        pheromone_intensity_grid[grid_x, grid_y] = min(1, pheromone_intensity_grid[grid_x, grid_y] + PHEROMONE_SPREAD_INTENSITY)

    def draw(self):
        # Rotate the image based on the angle
        rotated_image = pygame.transform.rotate(self.image, -self.angle-90)  # Negative to rotate clockwise
        new_rect = rotated_image.get_rect(center=self.rect.center)  # Adjust the position to avoid shifting
        
        # Blit the rotated image onto the screen. Blit is used to draw rotated images onto other objects (here the sceen)
        screen.blit(rotated_image, new_rect.topleft)

# Initializing a Clock - this sets the overall frame rate
clock = pygame.time.Clock()

# Initialize the FoodField instance
food_field = FoodField(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE)
# Initialize the smell grid
#smell_grid = np.zeros((SCREEN_WIDTH//GRID_SIZE, SCREEN_HEIGHT//GRID_SIZE)) # this is now handled within the food field class and passed to the ants

# Main loop
running = True
ants = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click to add food
                food_field.add_food_source(event.pos)
            elif event.button == 3:  # Right click to remove closest food
                mouse_x, mouse_y = event.pos
                closest_food = None
                min_distance = float('inf')

                for food in food_field.food_sources:
                    food_x, food_y = food.position
                    distance = math.hypot(food_x - mouse_x, food_y - mouse_y)

                    if distance < min_distance:
                        min_distance = distance
                        closest_food = food

                if closest_food and min_distance <= cropped_mushroom_image.get_width() // 2:
                    food_field.remove_food_source(closest_food)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # "s" key is pressed
                new_ant = Ant(ant_stack_position[0], ant_stack_position[1], food_field.smell_grid)
                ants.append(new_ant)
            elif event.key == pygame.K_d:  # "d" key is pressed
                if ants:
                    ants.pop(0)

    # Fill the background
    screen.fill(BACKGROUND_COLOR)
    screen.blit(background_image, (0, 0))

    global_pheromones_fading()

    # Draw the ant stack
    screen.blit(cropped_ant_stack_image, (ant_stack_position[0] - cropped_ant_stack_image.get_width() // 2, ant_stack_position[1] - cropped_ant_stack_image.get_height() // 2))

    # Update and draw food field
    food_field.update()
    food_field.draw(screen)

    # Move and draw ants, let them release pheromones
    for ant in ants:
        ant.move()
        ant.draw()
        ant.release_pheremones()

    pygame.display.flip()
    clock.tick(FRAMES_PER_SECOND)
