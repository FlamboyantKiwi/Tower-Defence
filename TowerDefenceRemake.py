import pygame
from base import Timer, TowerType, Button, sort_path, draw_list, get_local_pos
from levelInfo import MAP, TOWERS, PATH, get_colour
from sprites import Tile, Enemy, Tower
pygame.init()
Vector2 = pygame.math.Vector2
Colour = tuple[int,int,int]
Pos = tuple[int|float, int|float] | Vector2

# --- Configuration & Constants ---
BLOCK_SIZE = 30
COLS = 20  # How many blocks wide?
ROWS = 20  # How many blocks high?
UI_WIDTH = 200
MAP_WIDTH = COLS * BLOCK_SIZE 
MAP_HEIGHT = ROWS * BLOCK_SIZE 

SCREEN_WIDTH = MAP_WIDTH + UI_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()

STARTING_MONEY = 500
STARTING_LIVES = 20

ENEMY_HP = 20
ENEMY_SPEED = 1.5
ENEMY_BOUNTY = 10
WAVES_BREAK = 3 * FPS # Time between waves (seconds)
SPAWN_DELAY = 1 * FPS # Time between enemies spawning (seconds)

STARTING_ENEMIES = 5
ENEMIES_PER_WAVE = 2
ENEMY_HP_INCREASE = 5

BTN_SIZE = 50

WHITE = "#FFFFFF"
BLACK = "#000000"
UI_BG = "#32323C"       # Sidebar background
PANEL_BG = "#1E1E1E"    # Info panel background
GOLD = "#FFD700"        # Used for money/cost
GRAY_TEXT = "#969696"   # Used for subtext

class Spawner:
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
        self.enemies_to_spawn = STARTING_ENEMIES + (self.wave_number - 1 * ENEMIES_PER_WAVE)
        
        # Switch State - start creating enemies
        self.state = "SPAWNING"
        self.spawn_timer.activate()

    def spawn_enemy(self):
        # Increase Difficulty!
        # NOTE: Up to students how difficult they make it and which variables they increase. 
        # Examples:     (would be good to have values (e.g. 5, 1.2) as easy to change global variables
        hp = ENEMY_HP + (self.wave_number -1 * 5) 
        speed = ENEMY_SPEED + (self.wave_number -1 * 1.2)
        bounty = ENEMY_BOUNTY + (self.wave_number -1 * 2)
        self.manager.create_enemy(hp, speed, bounty)
        
    def get_info_text(self):
        if self.state == "COUNTDOWN":
            seconds_left = max(0, self.wave_timer.current_time // 60)
            return f"Next: {seconds_left}s"
        else:
            return f"WAVE {self.wave_number}"

class GameManager:
    def __init__(self, screen:pygame.Surface, map_data, global_rect):
        self.global_rect = pygame.Rect(global_rect)
        self.local_rect = pygame.Rect(0, 0, self.global_rect.width, self.global_rect.height)
        self.surface = screen.subsurface(self.global_rect)
        
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        
        # Entities
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.spawner = Spawner(self)
        
        # State
        self.selected_type = TOWERS["Archer"]

        # Map Setup
        self.grid = [] 
        self.path = []
        self.setup_map(map_data)

    def update(self, global_mouse_pos):
        local_mouse_pos = get_local_pos(global_mouse_pos, self.global_rect)
        self.spawner.update()
        
        # Pass enemies to towers so they can shoot
        for t in self.towers:
            self.money += t.update(local_mouse_pos, self.enemies)

        self.enemies.update()
        
        # Check for Game Over / Escaped Enemies
        for enemy in self.enemies:
            if enemy.escaped:
                self.enemies.remove(enemy)
                self.lives -= 1
                if self.lives <= 0: 
                    print("GAME OVER")

    def draw(self):
        # 1. Draw Tiles
        for row in self.grid:
            for tile in row:
                tile.draw(self.surface)

        # 2. Draw Towers
        for tower in self.towers:
            tower.draw(self.surface)
    
        # 3. Draw Enemies
        self.enemies.draw(self.surface)

    def click(self, global_mouse_pos):
        """ Handles clicks on the Game Map """
        if not self.global_rect.collidepoint(global_mouse_pos):
            return # Clicked outside the map

        # Convert to Local Coordinates
        local_pos = get_local_pos(global_mouse_pos, self.global_rect)
        col = local_pos[0] // BLOCK_SIZE
        row = local_pos[1] // BLOCK_SIZE
        
        #Skip if outside map
        if 0 > row >= ROWS or 0 > col >= COLS: 
            return

        tile = self.grid[row][col]
        
        if tile.tower:
            self.selected_object = tile.tower # Select existing
            
            # Simple Upgrade on click (for now)
            if self.can_afford(tile.tower.get_upgrade_cost()):
                tile.tower.upgrade()
                print(f"Upgraded to Level {tile.tower.level}")

        elif self.selected_type and tile.can_place(self.selected_type):
            # Build new
            if self.can_afford(self.selected_type.cost):
                tower = tile.add_tower(self.selected_type)
                self.towers.add(tower)
                print(f"Built {self.selected_type.name}")

    def get_hovered(self):
        for tower in self.towers:
            if tower.is_hovered: 
                return tower
        return None
    
    def can_afford(self, cost):
        if self.money >= cost:
            self.money -= cost
            return True
        print(f"Not enough money. Need: £{cost}")
        return False
        
    def setup_map(self, map_data):
        self.grid = []
        path_coords = []
        
        for row, tile_string in enumerate(map_data):
            tile_row = []
            for col, tile_value in enumerate(tile_string):
                # Simple color coding for the map
                c = get_colour(tile_value)
                if tile_value == PATH:   
                    path_coords.append((col, row))
                
                tile_row.append(Tile(col, row, tile_value, BLOCK_SIZE, colour=c))
            self.grid.append(tile_row)
            
        self.path = sort_path(path_coords, COLS, ROWS, BLOCK_SIZE)
        
    def create_enemy(self, hp, speed, bounty):
        new_enemy = Enemy(hp, speed, bounty, self.path)
        self.enemies.add(new_enemy)

class Interface:
    def __init__(self, screen:pygame.Surface, game_manager, global_rect):
        self.global_rect = pygame.Rect(global_rect)
        self.local_rect = pygame.Rect(0, 0, self.global_rect.width, self.global_rect.height)
        self.surface = screen.subsurface(self.global_rect)

        self.font = pygame.font.SysFont(None, 24)
        self.manager = game_manager
        
        self.buttons = Button.create_grid(
            towers=TOWERS, start_x=12, start_y=160, cols=3, 
            size=BTN_SIZE, gap=(10, 25), font=self.font, 
            selected_type=self.manager.selected_type)
        
        self.info_rect = pygame.Rect(10, 410, 180, 175)

    def update(self, mouse_pos):
        local_mouse = get_local_pos(mouse_pos, self.global_rect)
        for btn in self.buttons:
            btn.update(local_mouse)

    def draw(self):
        self.surface.fill(UI_BG) # Dark Sidebar Background
        # Draw dividing line
        pygame.draw.line(self.surface, WHITE, (0, 0), (0, self.local_rect.height), 4)

        stats = [
            f"Money: ${self.manager.money}",
            f"Lives: {self.manager.lives}",
            f"{self.manager.spawner.get_info_text()}",
            "", "TOWERS:"
        ]
        draw_list(self.surface, stats, (20, 20), self.font, line_height=30)

        # Draw Buttons
        for btn in self.buttons:
            btn.draw(self.surface, self.manager.money)

        # Info Panel
        item = self.manager.get_hovered() or self.manager.selected_type
        if item: 
            self.draw_info_panel(self.surface, item)

    def click(self, mouse_pos):
        local_mouse = get_local_pos(mouse_pos, self.global_rect)
        
        for btn in self.buttons:
            if btn.is_clicked(local_mouse):
                self.manager.selected_type = btn.type
                self.manager.selected_object = None # Deselect tower if we pick a blueprint
                print(f"Selected: {btn.type.name}")
                
                for b in self.buttons:
                    b.is_selected = False
                btn.is_selected = True

    def draw_info_panel(self, screen, item:Tower|TowerType):
        """ Draws the info box using the helper 'draw_list' function. """
        actual_type = getattr(item, "type", item)
        border_col = getattr(actual_type, "color", WHITE)
        pygame.draw.rect(screen, PANEL_BG, self.info_rect) 
        pygame.draw.rect(screen, border_col, self.info_rect, 2) 

        if not hasattr(item, "get_ui_details"):
            return
        
        info_list = item.get_ui_details()

        start_pos = (self.info_rect.x + 10, self.info_rect.y + 10)
        draw_list(screen, info_list, start_pos, self.font)


game = GameManager(screen, MAP, (0, 0, MAP_WIDTH, MAP_HEIGHT))
ui   = Interface(screen, game, (MAP_WIDTH, 0, UI_WIDTH, MAP_HEIGHT))

running = True
while running:
    # --- INPUT HANDLING ---
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click
                game.click(mouse_pos)
                ui.click(mouse_pos)

    game.update(mouse_pos)
    ui.update(mouse_pos)

    # draw
    game.draw()
    ui.draw()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
