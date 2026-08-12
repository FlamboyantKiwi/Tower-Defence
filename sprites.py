import pygame
from base import Timer, TowerType, Clickable, Info, UpgradeMult, get_center, load_surface
Vector2 = pygame.math.Vector2

ENEMY = "#FF0000"
GRID = "#323232" # or None to turn off 
TOWER_RANGE = "#FFFFFF32"

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
        if GRID is not None:
            pygame.draw.rect(screen, GRID, self.rect, 1)
    def can_place(self, tower_type:TowerType):
        return self.tower is None and self.type in tower_type.valid_tiles
    def add_tower(self, tower_type): # type: ignore
        """ Original Code! Without farms """
        self.tower = Tower(self.col, self.row, self.rect.size[0], tower_type)
        return self.tower
    def add_tower(self, tower_type:TowerType):  # noqa: F811
        """ Only needed if you're adding in the option to have Farms"""
        if tower_type.is_farm:
            self.tower = FarmTower(self.col, self.row, self.rect.size[0], tower_type)
        else:
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
    def update(self, mouse_pos, enemy_group): # type: ignore
        """ The main brain of the tower. Runs every frame. """
        # Handle clicking/hovering
        Clickable.update(self, mouse_pos)
        
        # Move arrows/bullets
        self.projectiles.update()
        bounty_earned = 0
        hits = pygame.sprite.groupcollide(self.projectiles, enemy_group, True, False)
        
        for bullet, enemies_hit in hits.items():
            for enemy in enemies_hit:
                # Apply damage to the enemy
                is_dead = enemy.hit(bullet.damage)
                
                # If enemy runs out of HP, kill it
                if is_dead: 
                    bounty_earned += enemy.bounty
                    enemy.kill() # Removes it from the game

        # Try to shoot
        self.cooldown.update() # Tick the timer down
        if not self.cooldown.is_active():
            # If we are ready to shoot...
            enemy = self.aim_at_enemy(enemy_group)
            if enemy:
                self.shoot(enemy)
                self.cooldown.activate() # Reset timer
        return bounty_earned
        
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
        new_arrow = Bullet.tower_bullet(self, target_enemy)
        self.projectiles.add(new_arrow)
    def draw_radius(self, screen):
        """ Helper to draw a transparent circle """
        radius = self.range
        # Make a transparent surface
        circle_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        # Draw a grey circle on it
        pygame.draw.circle(circle_surf, pygame.Color(TOWER_RANGE), (radius, radius), radius)
        # Paste it over the tower
        screen.blit(circle_surf, (self.center.x - radius, self.center.y - radius))

    def upgrade(self):
        """Applies the next level's stats to the tower."""
        next_stats = self.type.get_next_stats(self)
        
        # Access the stats using the Enum directly!
        self.damage = next_stats[UpgradeMult.DAMAGE]
        self.range = next_stats[UpgradeMult.RANGE]
        self.cooldown.duration = next_stats[UpgradeMult.COOLDOWN]
        
        self.level += 1
        
    def get_upgrade_cost(self) -> int:
        """Convenience method to fetch the cost of the next upgrade."""
        next_stats = self.type.get_next_stats(self)
        return next_stats[UpgradeMult.COST]

    def get_ui_details(self)-> list[Info]:
        # Calculate the 'Green' numbers (The next level stats)
        next_stats = self.type.get_next_stats(self)
        
        # Return the list
        return [
            Info(f"LVL {self.level} {self.type.name}", colour=self.type.color),
            Info(f"Dmg: {self.damage}",               next_value=next_stats[UpgradeMult.DAMAGE]),
            Info(f"Rng: {self.range}",                next_value=next_stats[UpgradeMult.RANGE]),
            Info(f"Cool: {self.cooldown.duration}",   next_value=next_stats[UpgradeMult.COOLDOWN]),
            Info(f"Upg: £{next_stats[UpgradeMult.COST]}", colour=(255, 215, 0), padding=10),
            Info("(Click to Upgrade)",        colour=(150, 150, 150))
        ]

class Bullet(pygame.sprite.Sprite):
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
        self.target_node = 0 # The index of the NEXT target in the list

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

        # Update the visual position
        self.rect.center = get_center(self.pos)
        
    def hit(self, damage):
        self.health -= damage
        return self.health <= 0 # did the enemy survive or die?


# Extra Optional Farm Sprite 
class FarmTower(Tower):
    def __init__(self, col, row, size, tower_type: TowerType):
        super().__init__(col, row, size, tower_type)
        # Repurpose 'damage' as our 'income' amount

    def update(self, mouse_pos, enemy_group):
        """ The money-making brain. """
        Clickable.update(self, mouse_pos)
        
        money_earned = 0
        
        self.cooldown.update() 
        if not self.cooldown.is_active():
            # Timer finished, Generate money instead of shooting
            money_earned += self.damage 
            self.cooldown.activate() # Reset timer

            print(f"Farm generated ${self.damage}!")

        # Send the paycheck back to the GameManager
        return money_earned

    def draw_radius(self, screen):
        pass # Farms don't shoot, so we override this to draw nothing

    def get_ui_details(self) -> list[Info]:
        """ Override the UI to say 'Income' instead of 'Damage' """
        next_stats = self.type.get_next_stats(self)
        
        return [
            Info(f"LVL {self.level} {self.type.name}", colour=self.type.color),
            Info(f"Income: ${self.damage}",           next_value=next_stats[UpgradeMult.DAMAGE]),
            Info(f"Speed: {self.cooldown.duration}",  next_value=next_stats[UpgradeMult.COOLDOWN]),
            Info(f"Upg: £{next_stats[UpgradeMult.COST]}", colour="#FFD700", padding=10), 
            Info("(Click to Upgrade)", colour="#969696")
        ]