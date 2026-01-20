#Tower Defence: Lesson 3: Clicking and Updating Screen
import pygame, sys
pygame.init()
pygame.font.init()
from TowerBase import UIManager, Tile, LEVEL_MAP, sort_path

#Screen Settings
MAP_WIDTH, MAP_HEIGHT = 600, 600 
UI_WIDTH = 200
BLOCK_SIZE = 30

# Calculated settings - Dont Touch
COLS, ROWS = MAP_WIDTH // BLOCK_SIZE, MAP_HEIGHT // BLOCK_SIZE

#Initialisation
screen = pygame.display.set_mode((MAP_WIDTH+UI_WIDTH, MAP_HEIGHT))
pygame.display.set_caption("Tower Defence")
clock = pygame.time.Clock()
Vector2 = pygame.math.Vector2
FPS = 60

#Modifiable Settings
STARTING_MONEY = 500
STARTING_LIVES = 20

# Colours
BG_COLOR = (0, 0, 0) # Black background
SIDEBAR_BG = (50, 50, 50) # Dark Grey for sidebar
TEXT_COLOR = (255, 255, 255) # Default White Text
ENEMY_COLOUR = (255, 0, 0) # Default Red Enemies

# Helper Function
def get_tile_coords(pos):
    """ Converts pixel coordinates (e.g., 35, 40) into grid coordinates (e.g., 1, 1).
        Integer Division (//) ignores remainders."""
    return (int(pos[0] // BLOCK_SIZE), int(pos[1] // BLOCK_SIZE))


class GameManager(UIManager):
    def __init__(self, map_data=LEVEL_MAP):
        # Initialize the UIManager (the parent class) with the map dimensions
        super().__init__(x=0, y=0, width=MAP_WIDTH, height=MAP_HEIGHT)
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        
        # Sprite Groups
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()

        # Build the level immediately when the game starts
        self.setup_map(map_data)
        
    def draw(self, screen):
        """ Draws the pre-rendered map surface onto the main screen surface. """
        # Draw the Grid Tiles
        for row in self.grid:
            for tile in row:
                tile.draw(screen)
    
    def update(self): 
        # NOTE: Parent Class will automatically do this, can just leave till later
        return True # game is still playing

    def click(self, pos):
        """ Handles mouse clicks on the map area. """
        col, row = get_tile_coords(pos)
        # For now, just prove we know where the user clicked
        print("Clicked Tile:", row, col)

    def setup_map(self, map): 
        # Iterate over the grid (row, col)
        self.grid = [] # The main List holding rows of Tile Objects
        path_coords = [] # Temporary List to store Un-Sorted Enemy Path Coordinates
        # Iterate through rows (Y-axis)
        for row, row_string in enumerate(map[:ROWS]):
            grid_row = []
            # Iterate through columns (X-axis) inside that row
            for col, key in enumerate(row_string[:COLS]):
                if key == 'P': 
                    color = (100, 50, 0)   # Brown
                    path_coords.append((col, row)) # Save coordinate for pathfinding    
                elif key == 'T': 
                    color = (0, 150, 20)   # Green
                elif key == 'B': 
                    color = (100, 100, 100) # Gray 
                else:   
                    color = (255, 0, 255) # Error Colour
                # Create the Tile object and add it to the temporary row list
                grid_row.append(Tile(col, row, key, BLOCK_SIZE, colour=color))
                # Add the finished row to the main grid
            self.grid.append(grid_row)
            # Organize the path coordinates from Start -> End
        self.path = sort_path(path_coords, COLS, ROWS, BLOCK_SIZE)

# Main Game Loop
# Create our Game Manager instance
game_manager = GameManager(LEVEL_MAP) 
# List of UI sections (Map, Sidebar, etc.)
sections = [game_manager]

playing = True
while playing:
    clock.tick(FPS)
    #Input Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        # Check for Mouse Clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Iterate through systems to see which one was clicked
            for ui in sections:
                if ui.is_clicked(event.pos):
                    ui.click(event.pos)
                    break # Stop checking other systems if one handled it

    # Updates
    if playing:
        # We update the game_manager variable to check if we lost (returns False)
        playing = game_manager.update()

    # Draw the map
    screen.fill(BG_COLOR)
    for ui in sections: # Ask every section to draw itself
        ui.draw(screen)
    pygame.display.update()

pygame.quit()       
sys.exit()