#Tower Defence: Lesson 13 - Adding UI Functionality
import pygame, sys
pygame.init()
pygame.font.init()
from TowerBase import UIManager, Tile, Sprite, Timer, BaseTower, TowerType, Button, LEVEL_MAP, TOWERS, sort_path

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

# Enemy Settings
ENEMY_HP = 20
ENEMY_SPEED = 1.5
ENEMY_BOUNTY = 10
WAVES_BREAK = 3 * FPS # Time between waves (seconds)
SPAWN_DELAY = 1 * FPS # Time between enemies spawning (seconds)

STARTING_ENEMIES = 5
ENEMIES_PER_WAVE = 2
ENEMY_HP_INCREASE = 5

# UI Settings
UI_BTN_SIZE = 60
UI_GAP = 20
UI_START_Y = 150

# Colours
BG_COLOR = (0, 0, 0) # Black background
SIDEBAR_BG = (50, 50, 50) # Dark Grey for sidebar
TEXT_COLOR = (255, 255, 255) # Default White Text
ENEMY_COLOUR = (255, 0, 0) # Default Red Enemies

def get_tile_coords(pos):
    return (int(pos[0] // BLOCK_SIZE), int(pos[1] // BLOCK_SIZE))
 
class GameManager(UIManager):
    def __init__(self, map_data=LEVEL_MAP):
        super().__init__(x=0, y=0, width=MAP_WIDTH, height=MAP_HEIGHT)
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
            enemy.update()
            if enemy.breached:
                self.enemies.remove(enemy)
                self.lives -= 1
                if self.lives <= 0: 
                    print("GAME OVER")
        return self.lives > 0

    def click(self, pos):
        col, row = get_tile_coords(pos)
        
        print("Clicked Tile:", row, col)
        clicked_tile = self.grid[row][col]
        # SCENARIO 1: UPGRADE
        if clicked_tile.tower:
            cost = clicked_tile.tower.get_upgrade_cost()
            if self.attempt_buy(cost):
                clicked_tile.tower.upgrade()
                print(f"Upgraded to Level {clicked_tile.tower.level}")
        elif clicked_tile.can_place(self.selected_type):
            cost = self.selected_type.cost
            
            if self.attempt_buy(cost): 
                # Create new tower
                new_tower = Tower(col, row, self.selected_type)
                self.towers.add(new_tower)
                clicked_tile.tower = new_tower
                print(f"Built {self.selected_type.name}")
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
        self.path = sort_path(path_coords, COLS, ROWS, BLOCK_SIZE)
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
        self.enemies.add(Enemy(hp, speed, bounty, self.path))

class Enemy(Sprite):
    def __init__(self, health:int, speed:float, bounty:int, path, path_index:int = 0):
        super().__init__(0,0, BLOCK_SIZE, colour=ENEMY_COLOUR) 
        #Reposition enemy
        self.pos = Vector2(path[path_index])
        self.rect.center = (int(self.pos.x), int(self.pos.y))  
        # NOTE: code will still work without this line (self.rect.center)
        # Enemy will just spawn at topleft of screen (Update function will fix this)
        
        #Movement Variables
        self.path = path
        self.path_index = path_index
        self.target_node = 0

        #Enemy Stats
        self.health = health
        self.speed = speed
        self.bounty = bounty
        self.breached = False
                
    def update(self):
        """ Moves the enemy along the path. """
        # If enemy reached the end of the path
        if self.target_node >= len(self.path):
            self.breached = True
            return # Stop function to prevent crashing
        
        # Calculate direction to the next path node
        target_pos = Vector2(self.path[self.target_node])
        # Vector Math: Target - Current = Direction
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

class Tower(BaseTower):
    def __init__(self, col, row, tower_type:TowerType = TOWERS["Archer"]):
        super().__init__(col, row, BLOCK_SIZE, tower_type.color)
        
        # Setup Game Variables 
        self.type = tower_type
        self.level = 1
        
        # Copy stats from TowerType
        self.range = tower_type.range
        self.damage = tower_type.damage
        self.cooldown_timer = Timer(tower_type.cooldown_frames)
        
        self.projectiles = pygame.sprite.Group()
        
    def draw(self, screen):
        """Draws the tower and its projectiles."""
        #Draw Range (if hovered over) 
        if self.is_hovered or self.is_selected:
            self.draw_range(screen)
        # Draw tower 
        screen.blit(self.image, self.rect)
        # Draw the tower's projectiles
        self.projectiles.draw(screen)
    def update(self, mouse_pos):
        super().update(mouse_pos) # Checks if mouse is hovering over us
        self.projectiles.update() # Update all projectiles
        
        # Shooting Logic - Reloading
        self.cooldown_timer.update() 
        if not self.cooldown_timer.is_active():
            target = self.find_target()
            if target:
                self.fire(target)
                self.cooldown_timer.activate()

        # Collision logic - did any projectiles hit any enemies
        hits = pygame.sprite.groupcollide(game_manager.enemies, self.projectiles, False, True)
        for enemy, projectiles_hit in hits.items():
            # Calculate total damage
            total_damage = sum(p.damage for p in projectiles_hit)
            if enemy.hit(total_damage):
                # If hit() returns True, the enemy died
                game_manager.enemies.remove(enemy)
                game_manager.money += enemy.bounty

    def find_target(self):
        """ Finds the enemy closest to the exit (highest path_index) within range. """
        best_target = None
        furthest_position = -1 # Position closest to the end
        
        # Iterate (loop) over all enemies in the game
        for enemy in game_manager.enemies:
            # Check distance between tower center and enemy center
            dist = self.center_pos.distance_to(enemy.rect.center)
            if dist <= self.range:
                # Prioritize enemy closest to the end (highest path index)
                if enemy.path_index > furthest_position:
                    furthest_position = enemy.path_index
                    best_target = enemy
        return best_target
    def fire(self, target):
        """Creates a Projectile aimed at the given target."""
        target_pos = Vector2(target.rect.center)
        # Calculate angle to point the projectile
        direction = target_pos - self.center_pos
        angle = direction.angle_to(Vector2(1, 0)) 
        # Create Projectile
        self.projectiles.add(Projectile(self, angle))
    
    def get_upgrade_cost(self):
        # Calculates upgrade cost based current cost and level
        return int(self.type.cost * self.level * 0.7)
    def get_upgraded_damage(self):
        return int(self.damage * 1.5)
    def get_upgraded_range(self):
        return self.range + 15
    def get_upgraded_cooldown(self):
        return int(self.cooldown_timer.duration * 0.9)

    def upgrade(self):
        """ Applies new upgrade stats """      
        self.damage = self.get_upgraded_damage()
        self.range = self.get_upgraded_range()
        self.cooldown_timer.duration = self.get_upgraded_cooldown()
        self.level += 1

class Projectile(Sprite):
    def __init__(self, owner, angle):
        self.damage = owner.damage
        self.range_limit = owner.range
        
        # 2. Get visual stats from the tower's "type"
        stats = owner.type
        speed = stats.proj_speed
        size = stats.proj_size
        color = stats.color
        
        # 3. Setup position (start at the tower's center)
        x, y = owner.center_pos       
        super().__init__(x, y, size, colour=color)
        self.spawn_pos = Vector2(x, y)
        self.pos = self.spawn_pos
        self.velocity = Vector2(speed, 0).rotate(-angle)
        
    def update(self):
        # Update position
        self.pos += self.velocity
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # CLEANUP: Delete bullet if it goes past a certain range
        if self.pos.distance_to(self.spawn_pos) > self.range_limit:
            self.kill() # Removes sprite from all groups

class Interface(UIManager):
    def __init__(self, game_manager):
        super().__init__(MAP_WIDTH, 0, UI_WIDTH, MAP_HEIGHT)
        self.font = pygame.font.SysFont(None, 24)
        self.manager = game_manager
        self.buttons = []
        self.create_buttons()

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)
        return True
            
    def draw(self, screen):
        # Sidebar Background
        pygame.draw.rect(screen, SIDEBAR_BG, self.rect)
        
        # Stats Text
        money = self.manager.money
        self.draw_text(screen, f"Money: ${money}", (20, 20))
        self.draw_text(screen, f"Lives: {self.manager.lives}", (20, 60))
        
        # Build Buttons
        self.draw_text(screen, "TOWERS", (UI_WIDTH//2, 120), center=True)
        for btn in self.buttons:
            btn.draw(screen, money)

        # Info Panel
        item_to_draw = self.manager.get_hovered() or self.manager.selected_type
        if item_to_draw:
            self.draw_info_panel(screen, item_to_draw, int(money))

    def click(self, pos):
        """  Handles UI clicks. Returns True even if no button was pressed. """
        for btn in self.buttons:
            if btn.is_clicked(pos):
                # Update Game Logic
                self.manager.selected_type = btn.type
                print(f"Selected: {btn.type.name}")
                
                # Update Visuals
                for other_btn in self.buttons:
                    other_btn.is_selected = False 
                btn.is_selected = True            

    def create_buttons(self):            
        for i, t_type in enumerate(TOWERS.values()):
            # Calculate Grid Position
            col = i % 2 
            row = i // 2
            
            # Calculate Pixel Position
            x = MAP_WIDTH + UI_GAP + (col * (UI_BTN_SIZE + UI_GAP))
            y = UI_START_Y + (row * (UI_BTN_SIZE + UI_GAP))
            
            is_selected = self.manager.is_selected(t_type)

            button = Button(x, y, UI_BTN_SIZE, t_type, self.font, is_selected)
            self.buttons.append(button)


game_manager = GameManager() 
interface = Interface(game_manager)
sections = [game_manager, interface]
playing = True
while playing:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Iterate through systems to see which one was clicked
            for ui in sections:
                if ui.is_clicked(event.pos):
                    ui.click(event.pos)
                    break # Stop checking other systems if one handled it

    # Updates
    if playing:
        playing = game_manager.update()
        interface.update()

    # Draw the map
    screen.fill(BG_COLOR)
    for ui in sections:
        ui.draw(screen)
    pygame.display.update()

pygame.quit()       
sys.exit()