#Tower Defence: Lesson 1: Setup Screen
import pygame, sys
pygame.init()
pygame.font.init()
from TowerBase import *

#Screen Dimensions
MAP_WIDTH, MAP_HEIGHT = 600, 600 
UI_WIDTH = 200
BLOCK_SIZE = 30 # The pixel size of one grid square

# Calculated settings - Dont Touch
# We divide the map width by the block size to know how many columns we have.
# 600 / 30 = 20 Columns
COLS, ROWS = MAP_WIDTH // BLOCK_SIZE, MAP_HEIGHT // BLOCK_SIZE

# Create the window
# We add UI_WIDTH to the width so we have space for the menu on the side
screen = pygame.display.set_mode((MAP_WIDTH+UI_WIDTH, MAP_HEIGHT))
pygame.display.set_caption("Tower Defence")
# Clock controls how fast the game runs
clock = pygame.time.Clock()
FPS = 60

# Colour Palette
#RGB Values: (Red, Green, Blue) -> 0 to 255
BG_COLOR = (0, 0, 0) # Black background
SIDEBAR_BG = (50, 50, 50) # Dark Grey for sidebar
TEXT_COLOR = (255, 255, 255) # Default White Text
ENEMY_COLOUR = (255, 0, 0) # Default Red Enemies

# Helper Function
def get_tile_coords(pos):
    """ Converts pixel coordinates (e.g., 35, 40) into grid coordinates (e.g., 1, 1).
        Integer Division (//) ignores remainders."""
    return (int(pos[0] // BLOCK_SIZE), int(pos[1] // BLOCK_SIZE))


playing = True
while playing:
    # Ensure the game runs at 60 FPS
    clock.tick(FPS) 
    #Input Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False


    # Draw a new Screen and update
    screen.fill(BG_COLOR)
    pygame.display.update()

#Exit code - ensures python/pygame close correctly
pygame.quit()       
sys.exit()