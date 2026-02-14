import pygame
pygame.init()
Vector2 = pygame.math.Vector2
Colour = tuple[int,int,int]
Pos = tuple[int|float, int|float] | Vector2
from NewBase import Timer, TowerType, Clickable, Button, Info, get_center, load_surface, get_grid_pos, sort_path, draw_text, draw_list, get_local_pos
from levelInfo import MAP, TOWERS
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

GRID_LINES = True
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

UI_BG = (50,50,60) # dark sidebar background
ENEMY = (255, 0, 0)
GRID = (50,50,50)


class Tile(pygame.sprite.Sprite):
    def __init__(self, col:int, row:int, type:str, size:int, image_name=None, colour=None):
        self.col = col
        self.row = row
        self.type = type
        self.tower = None 
        self.image = load_surface((size,size), image_name, colour)
        self.rect = self.image.get_rect(x=col*size, y=row*size)
    def draw(self, screen:pygame.Surface):
        screen.blit(self.image, self.rect)
        if GRID_LINES:
            pygame.draw.rect(screen, GRID, self.rect, 1)
    def can_place(self, tower_type:TowerType):
        return self.tower is None and self.type in tower_type.valid_tiles
    def add_tower(self, tower_type):
        self.tower = Tower(self.col, self.row, self.rect.size[0], tower_type)
        return self.tower

class Tower(pygame.sprite.Sprite, Clickable):
    def __init__(self, col, row, size, tower_type:TowerType):
        # Setup Sprite
        super().__init__()
        self.image = load_surface((size,size), tower_type.image_file, tower_type.color)
        self.rect = self.image.get_rect(x=col*size, y=row*size)
        self.center = pygame.math.Vector2(self.rect.center) 
        # makes it easier to shoot projectiles later

        # Setup Interaction
        Clickable.__init__(self, self.rect)

        # Setup Stats
        self.level = 1
        self.type = tower_type
        self.damage = tower_type.damage
        self.range = tower_type.range

        # Setup Tools
        self.cooldown = Timer(tower_type.cooldown_frames)
        self.projectiles = pygame.sprite.Group()
    def draw(self, screen):
        # Draw the Range Circle if we hover over the tower
        if self.is_hovered:
            self.draw_radius(screen)

        # Draw the Tower
        screen.blit(self.image, self.rect)

        # Draw all arrows/bullets
        self.projectiles.draw(screen)
    def update(self, mouse_pos, enemy_group):
        """ The main brain of the tower. Runs every frame. """
        # Handle clicking/hovering
        Clickable.update(self, mouse_pos)
        
        # Move arrows/bullets
        self.projectiles.update()

        hits = pygame.sprite.groupcollide(self.projectiles, enemy_group, True, False)
        
        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
                # Apply damage to the enemy
                is_dead = enemy.hit(bullet.damage)
                
                # If enemy runs out of HP, kill it
                if is_dead: enemy.kill() # Removes it from the game

        # Try to shoot
        self.cooldown.update() # Tick the timer down
        if not self.cooldown.is_active():
            # If we are ready to shoot...
            enemy = self.aim_at_enemy(enemy_group)
            if enemy:
                self.shoot(enemy)
                self.cooldown.activate() # Reset timer

    def aim_at_enemy(self, enemy_group:list['Enemy']):
        """ scan for the enemy closest to the exit """
        best_target = None
        closest_to_win = -1 # Higher path_index means closer to winning

        for enemy in enemy_group:
            # Check Distance
            distance = self.center.distance_to(enemy.rect.center)
            if distance <= self.range:
                # Check if this enemy is further ahead than the last one we found
                if enemy.target_node> closest_to_win:
                    closest_to_win = enemy.target_node
                    best_target = enemy
        
        return best_target
    def shoot(self, target_enemy):
        new_arrow = Projectile.tower_bullet(self, target_enemy)
        self.projectiles.add(new_arrow)
    def draw_radius(self, screen):
        """ Helper to draw a transparent circle """
        radius = self.range
        # Make a transparent surface
        circle_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        # Draw a grey circle on it
        pygame.draw.circle(circle_surf, (100, 100, 100, 100), (radius, radius), radius)
        # Paste it over the tower
        screen.blit(circle_surf, (self.center.x - radius, self.center.y - radius))
    
    def get_upgrade_cost(self):
        return int(self.type.cost * self.level * 0.7)

    def get_upgraded_damage(self):
        return int(self.damage * 1.5)

    def get_upgraded_range(self):
        return self.range + 15

    def get_upgraded_cooldown(self):
        return int(self.cooldown.duration * 0.9)

    def upgrade(self):
        """ Applies new upgrade stats """      
        self.damage = self.get_upgraded_damage()
        self.range = self.get_upgraded_range()
        self.cooldown.duration = self.get_upgraded_cooldown()
        self.level += 1

    def get_ui_details(self)-> list[Info]:
        # Calculate the 'Green' numbers (The next level stats)
        next_dmg  = self.get_upgraded_damage()
        next_rng  = self.get_upgraded_range()
        next_cool = self.get_upgraded_cooldown()
        
        # Return the list
        return [
            Info(f"LVL {self.level} {self.type.name}", colour=self.type.color),
            Info(f"Dmg: {self.damage}",       next_value=next_dmg),
            Info(f"Rng: {self.range}",        next_value=next_rng),
            Info(f"Cool: {self.cooldown.duration}", next_value=next_cool),
            Info(f"Upg: ${self.get_upgrade_cost()}", colour=(255, 215, 0), padding=10),
            Info("(Click to Upgrade)",        colour=(150, 150, 150))
        ]

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos:Vector2, target_pos:Vector2, damage, speed, range, image):
        super().__init__()

        self.damage = damage
        self.speed = speed
        self.range = range
        self.image = image
        self.rect = self.image.get_rect(center=get_center(start_pos))

        self.pos = Vector2(start_pos)
        self.start_pos = Vector2(start_pos)

        direction = target_pos - start_pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = Vector2(0,0)
    def update(self):
        self.pos += self.velocity
        self.rect.center = get_center(self.pos)

        dist = self.pos.distance_to(self.start_pos)
        if dist > self.range:
            self.kill()
    @classmethod
    def tower_bullet(cls, tower:Tower, target_enemy):
        """ Factory Method: Takes a Tower and an Enemy and returns a ready-to-use Projectile."""
        # Unpack the Raw Data
        start_pos = tower.center
        target_pos = Vector2(target_enemy.rect.center)
        damage = tower.damage
        speed = tower.type.proj_speed
        range_limit = tower.range
        
        # Create the Visual
        size = tower.type.proj_size
        color = tower.type.color
        image_name = tower.type.proj_image_file
        image = load_surface((size, size), image_name, color)
        
        # Call the main __init__ with the raw data
        # 'cls' just means 'Projectile'
        return cls(start_pos, target_pos, damage, speed, range_limit, image)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, health:int, speed:float, bounty:int, path_coords:list[Vector2]):
        super().__init__() 
        #Movement Variables
        self.path = path_coords
        self.pos = Vector2(self.path[0])
        self.target_node = 1 # The index of the NEXT target in the list

        # Visuals
        self.image = load_surface((20,20), colour=ENEMY)
        self.rect = self.image.get_rect(center=self.pos)

        #Enemy Stats
        self.health = health
        self.speed = speed
        self.bounty = bounty
        self.escaped = False
                
    def update(self):
        """ Moves the enemy along the path. """
        # If enemy reached the end of the path
        if self.target_node >= len(self.path):
            self.escaped = True
            return # Stop function to prevent crashing
        
        # Calculate direction to the next path node
        target_pos = self.path[self.target_node]
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

        # Update the visual position
        self.rect.center = get_center(self.pos)
        
    def hit(self, damage):
        self.health -= damage
        return self.health <= 0 # did the enemy survive or die?

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
    def __init__(self, map_data, global_rect:pygame.Rect):
        self.global_rect = global_rect
        self.local_rect = pygame.Rect(0, 0, global_rect.width, global_rect.height)

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
            t.update(local_mouse_pos, self.enemies)

        self.enemies.update()
        
        # Check for Game Over / Escaped Enemies
        for enemy in self.enemies:
            if enemy.escaped:
                self.enemies.remove(enemy)
                self.lives -= 1
                if self.lives <= 0: print("GAME OVER")

    def draw(self, screen):
        # 1. Draw Tiles
        for row in self.grid:
            for tile in row:
                tile.draw(screen)

        # 2. Draw Towers
        for tower in self.towers:
            tower.draw(screen)
    
        # 3. Draw Enemies
        self.enemies.draw(screen)

    def click(self, global_mouse_pos):
        """ Handles clicks on the Game Map """
        if not self.global_rect.collidepoint(global_mouse_pos):
            return # Clicked outside the map

        # 2. Convert to Local Coordinates
        local_pos = get_local_pos(global_mouse_pos, self.global_rect)
        col = local_pos[0] // BLOCK_SIZE
        row = local_pos[1] // BLOCK_SIZE
        
        if 0 > row >= ROWS or 0 > col >= COLS: return

        tile = self.grid[row][col]
        
        if tile.tower:
            self.selected_object = tile.tower # Select existing
            
            # Simple Upgrade on click (for now)
            cost = tile.tower.get_upgrade_cost()
            if self.money >= cost:
                self.money -= cost
                tile.tower.upgrade()
                print(f"Upgraded to Level {tile.tower.level}")

        elif self.selected_type and tile.can_place(self.selected_type):
            # Build new
            if self.money >= self.selected_type.cost:
                self.money -= self.selected_type.cost
                tower = tile.add_tower(self.selected_type)
                self.towers.add(tower)
                print(f"Built {self.selected_type.name}")

    def get_hovered(self):
        for tower in self.towers:
            if tower.is_hovered: return tower
        return None

    def setup_map(self, map_data):
        self.grid = []
        path_coords = []
        
        for row_idx, row_str in enumerate(map_data):
            tile_row = []
            for col_idx, char in enumerate(row_str):
                # Simple color coding for the map
                if char == 'P':   
                    c = (194, 178, 128) # Sand/Path
                    path_coords.append((col_idx, row_idx))
                elif char == 'T': 
                    c = (34, 139, 34)   # Grass
                elif char == 'B': 
                    c = (100, 100, 100) # Base/Block
                else:             
                    c = (255, 0, 255)
                
                tile_row.append(Tile(col_idx, row_idx, char, BLOCK_SIZE, colour=c))
            self.grid.append(tile_row)
            
        self.path = sort_path(path_coords, COLS, ROWS, BLOCK_SIZE)
    def create_enemy(self, hp, speed, bounty):
        new_enemy = Enemy(hp, speed, bounty, self.path)
        self.enemies.add(new_enemy)

class Interface:
    def __init__(self, game_manager, global_rect:pygame.Rect):
        # We assume this UI is drawn on a subsurface starting at (0,0)
        self.global_rect = global_rect
        self.local_rect = pygame.Rect(0, 0, global_rect.width, global_rect.height)

        self.font = pygame.font.SysFont(None, 24)
        self.manager = game_manager
        
        self.buttons = Button.create_grid(
            towers=TOWERS, start_x=12, start_y=160, cols=3, 
            size=BTN_SIZE, gap=(10, 25), font=self.font)
        self.info_rect = pygame.Rect(10, 410, 180, 175)

    def update(self, mouse_pos):
        for btn in self.buttons:
            btn.update(mouse_pos)

    def draw(self, screen):
        screen.fill(UI_BG) # Dark Sidebar Background
        # Draw dividing line
        pygame.draw.line(screen, (255, 255, 255), (0, 0), (0, self.local_rect.height), 4)

        stats = [
            f"Money: ${self.manager.money}",
            f"Lives: {self.manager.lives}",
            f"{self.manager.spawner.get_info_text()}",
            "", "TOWERS:"
        ]
        draw_list(screen, stats, (20, 20), self.font, line_height=30)

        # Draw Buttons
        for btn in self.buttons:
            btn.draw(screen, self.manager.money)

        # Info Panel
        item = self.manager.get_hovered() or self.manager.selected_type
        if item: self.draw_info_panel(screen, item)

    def click(self, mouse_pos):
        for btn in self.buttons:
            if btn.is_clicked(mouse_pos):
                self.manager.selected_type = btn.type
                self.manager.selected_object = None # Deselect tower if we pick a blueprint
                print(f"Selected: {btn.type.name}")
                
                for b in self.buttons: b.is_selected = False
                btn.is_selected = True

    def draw_info_panel(self, screen, item:Tower|TowerType):
        """ Draws the info box using the helper 'draw_list' function. """
        actual_type = getattr(item, "type", item)
        border_col = getattr(actual_type, "color", (255, 255, 255))
        pygame.draw.rect(screen, (30,30,30), self.info_rect) 
        pygame.draw.rect(screen, border_col, self.info_rect, 2) 

        if not hasattr(item, "get_ui_details"):
            return
        
        info_list = item.get_ui_details()

        start_pos = (self.info_rect.x + 10, self.info_rect.y + 10)
        draw_list(screen, info_list, start_pos, self.font)


map_rect_global = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
ui_rect_global  = pygame.Rect(MAP_WIDTH, 0, UI_WIDTH, MAP_HEIGHT)

map_surface = screen.subsurface(map_rect_global)
ui_surface  = screen.subsurface(ui_rect_global)

game = GameManager(MAP, map_rect_global)
ui   = Interface(game, ui_rect_global)

running = True
while running:
    # --- INPUT HANDLING ---
    global_mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click
                game.click(global_mouse_pos)
                ui.click(global_mouse_pos)

    game.update(global_mouse_pos)
    ui.update(global_mouse_pos)

    # --- DRAW PHASE ---
    # Note: We draw to the subsurfaces, NOT the main screen!
    game.draw(map_surface)
    ui.draw(ui_surface)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
