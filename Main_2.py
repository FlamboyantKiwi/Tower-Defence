#Tower Defence
import pygame, sys
pygame.init()
pygame.font.init()
from TowerBase import BaseSystem, Tile, LEVEL_MAP, TOWERS

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

#Modifiable Settings
STARTING_MONEY = 500
STARTING_LIVES = 20

# Colours
BG_COLOR = (0, 0, 0) # Black background
SIDEBAR_BG = (50, 50, 50) # Dark Grey for sidebar
TEXT_COLOR = (255, 255, 255) # Default White Text
ENEMY_COLOUR = (255, 0, 0) # Default Red Enemies

def get_tile_coords(pos):
    return (pos[0] // BLOCK_SIZE, pos[1] // BLOCK_SIZE)
 

class GameManager(BaseSystem):
    def __init__(self, map_data=LEVEL_MAP):
        super().__init__(x=0, y=0, width=MAP_WIDTH, height=HEIGHT)
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()

        self.selected_type = TOWERS["Archer"] # Default Tower

        self.grid = [] # The List of Tile Objects
        self.path = [] # Enemy Path Coordinates
        self.setup_map(map_data)
        
    def draw(self, screen):
        """ Draws the pre-rendered map surface onto the main screen surface. """
        # Draw the Grid Tiles
        for row in self.grid:
            for tile in row:
                tile.draw(screen)

        for tower in self.towers:
            tower.draw(screen)
    
        self.enemies.draw(screen)
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.towers.update(mouse_pos)

        return self.lives > 0
    def click(self, mouse_pos):
        col, row = get_tile_coords(mouse_pos)
        
        print("Clicked Tile:", row, col)

    def attempt_buy(self, cost):
        """ Checks if we can afford cost (of tower) """
        if self.money >= cost:
            self.money -= cost
            return True
        else:
            print(f"Not enough money! Need ${cost}")
            return False

    def setup_map(self, map): 
        # Iterate over the grid (row, col)
        path_coords = []
        for row, row_string in enumerate(map[:ROWS]):
            grid_row = []
            for col, key in enumerate(row_string[:COLS]):
                color = (100, 100, 100) # Default Gray
                if key == 'T': color = (0, 150, 20)   # Green
                elif key == 'P':
                    color = (100, 50, 0)   # Brown
                    path_coords.append((col, row)) # Save coordinate for pathfinding                    

                grid_row.append(Tile(col, row, key, BLOCK_SIZE, colour=color))
            self.grid.append(grid_row)
        self.path = self.sort_path(path_coords, COLS, ROWS, BLOCK_SIZE)
       
    def get_hovered(self):
        for tower in self.towers:
            if tower.is_hovered:
                return tower
        return None
    def is_selected(self, tower_type):
        """ Returns True if the given tower type is the one currently active. """
        if self.selected_type == tower_type:
            return True
        else:
            return False




game_manager = GameManager(LEVEL_MAP) 

playing = True
while playing:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Iterate through systems to see which one was clicked
            for ui in [game_manager]:
                if ui.is_clicked(event.pos):
                    ui.click(event.pos)
                    break # Stop checking other systems if one handled it

    # Updates
    if playing:
        playing = game_manager.update()

    # Draw the map
    screen.fill(BG_COLOR)
    for ui in [game_manager]:
        ui.draw(screen)
    pygame.display.update()

pygame.quit()       
sys.exit()