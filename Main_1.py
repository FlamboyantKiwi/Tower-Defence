#Tower Defence
import pygame, sys
pygame.init()
pygame.font.init()
from TowerBase import *

#Screen Settings
WIDTH, HEIGHT = 800, 600 
BLOCK_SIZE = 30
UI_WIDTH = 200

# Calculated settings - Dont Touch
MAP_WIDTH = WIDTH - UI_WIDTH
COLS, ROWS = MAP_WIDTH // BLOCK_SIZE, HEIGHT // BLOCK_SIZE

#Initialisation
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defence")
clock = pygame.time.Clock()
Vector2 = pygame.math.Vector2
FPS = 60

# Colours
BG_COLOR = (0, 0, 0) # Black background
SIDEBAR_BG = (50, 50, 50) # Dark Grey for sidebar
TEXT_COLOR = (255, 255, 255) # Default White Text
ENEMY_COLOUR = (255, 0, 0) # Default Red Enemies

playing = True
while playing:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False


    # Draw the map
    screen.fill(BG_COLOR)
    pygame.display.update()

pygame.quit()       
sys.exit()