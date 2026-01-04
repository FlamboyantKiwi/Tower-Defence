#Tower Defence
import pygame, sys
pygame.init()
pygame.font.init()
from TowerBase import BaseSystem, Tile, Sprite, Timer, LEVEL_MAP, TOWERS

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

# Enemy Settings
ENEMY_HP = 20
ENEMY_SPEED = 1.5
ENEMY_BOUNTY = 10
WAVES_BREAK = 3 * FPS # Time between waves (seconds)
SPAWN_DELAY = 1 * FPS # Time between enemies spawning (seconds)

STARTING_ENEMIES = 5
ENEMIES_PER_WAVE = 2
ENEMY_HP_INCREASE = 5

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

        self.spawner = EnemySpawner(self)
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
        self.spawner.update()

        # Enemy Update & Escape Check
        for enemy in self.enemies:
            status = enemy.update()
            if status == 'escaped':
                self.enemies.remove(enemy)
                self.lives -= 1
                if self.lives <= 0: 
                    print("GAME OVER")
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
    def create_enemy(self, hp, speed, bounty):
        start_pos = self.path[0]
        new_enemy = Enemy(start_pos.x, start_pos.y, hp, speed, bounty)
        self.enemies.add(new_enemy)
       
class Enemy(Sprite):
    def __init__(self, x, y, health:int, speed:float, bounty:int, path_index:int = 0):
        super().__init__(x, y, BLOCK_SIZE, colour=ENEMY_COLOUR)
        
        #Movement Variables
        self.pos = Vector2(x, y) 
        self.path_index = path_index
        self.target_node = 0

        #Enemy Stats
        self.health = health
        self.speed = speed
        self.bounty = bounty
        
    def update(self):
        """ Moves the enemy along the path. Returns 'escaped' or 'moving' """
        # If enemy reached the end of the path
        if self.target_node >= len(game_manager.path):
            return 'escaped'
        
        # Calculate direction to the next path node
        target_pos = Vector2(game_manager.path[self.target_node])
        direction = target_pos - self.pos
       
        # Movement Logic
        if direction.length() > self.speed:
            # Move towards the target at the current speed
            self.pos += direction.normalize() * self.speed
        else:
            # We are close, "snap" to the node and continue to next node
            self.pos = target_pos
            self.target_node += 1
            self.path_index = self.target_node

        # Update the visual position
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        return 'moving' # Indicate normal movement

    def hit(self, damage):
        self.health -= damage
        return self.health <= 0 # enemy died

class EnemySpawner:
    def __init__(self, game_manager):
        self.manager = game_manager
        self.wave_number = 0
        self.enemies_to_spawn = 0
        self.state = "COUNTDOWN" 
        
        self.wave_timer = Timer(WAVES_BREAK, start_active=True)
        self.spawn_timer = Timer(SPAWN_DELAY, start_active=False)

    def update(self):
        # Countdown to next wave
        if self.state == "COUNTDOWN":
            if self.wave_timer.update(): # Timer finished?
                self.start_new_wave()

        # LOGIC 2: Currently spawning enemies
        elif self.state == "SPAWNING":
            if self.spawn_timer.update():
                self.spawn_enemy()
                self.enemies_to_spawn -= 1
                
                if self.enemies_to_spawn > 0:
                    self.spawn_timer.activate() # Reset for next enemy
                else:
                    self.state = "WAITING"

        # Waiting for player to kill everyone
        elif self.state == "WAITING":
            if len(self.manager.enemies) == 0:
                # Wave cleared! Start countdown again
                self.state = "COUNTDOWN"
                self.wave_timer.activate()

    def start_new_wave(self):
        self.wave_number += 1
        print(f"Wave {self.wave_number} Started!")
        
        # Increase Difficulty: Add more enemies each wave
        self.enemies_to_spawn = STARTING_ENEMIES + (self.wave_number * ENEMIES_PER_WAVE)
        
        self.state = "SPAWNING"
        self.spawn_timer.activate()

    def spawn_enemy(self):
        # Increase Difficulty: Increase Enemy HP each wave
        hp = ENEMY_HP + (self.wave_number * 5)
        self.manager.create_enemy(hp, ENEMY_SPEED, ENEMY_BOUNTY)
    @property
    def get_info_text(self):
        if self.state == "COUNTDOWN":
            seconds_left = max(0, self.wave_timer.current_time // 60)
            return f"Next: {seconds_left}s"
        else:
            return f"WAVE {self.wave_number}"


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
        """if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # Spawn Enemy on click!
            game_manager.create_enemy(ENEMY_HP, ENEMY_SPEED, ENEMY_BOUNTY)"""
                 
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