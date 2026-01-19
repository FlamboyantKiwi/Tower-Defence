import pygame, os
from dataclasses import dataclass, field
Vector2 = pygame.math.Vector2
Surf = pygame.surface.Surface
Colour = tuple[int,int,int]
Pos = tuple[int|float, int|float] | Vector2

FOLDER_NAME = "Assets"
GRID_LINES = True

# --- COLOURs ---
AFFORDABLE = (0, 255, 0) # Green
EXPENSIVE = (255, 100, 100) # Red
INFO_PANEL = (60, 60, 60) # Dark Grey
TEXT = (255, 255, 255) # White
UPGRADE = (0, 255, 0) # Green Arrow Colour
FALLBACK = (255, 0, 255) # Hot Pink Error Colour 
SELECTED = (255, 255, 0) # Yellow
UNSELECTED = (0,0,0) # Black
RANGE = (100, 100, 100, 100) # Has 4th/alpha value: transparency amount
HIGHLIGHT = (255, 255, 255)
# --- Helper Functions ---
def load_colour_surface(colour:Colour, size:tuple[int,int]):
    """ Creates a plain colored square """
    surf = pygame.Surface(size)
    surf.fill(colour)
    return surf
def load_image(filename:str|None, size:tuple[int,int], fallback_colour:Colour):
    # No filename, use colour instead
    if not filename: 
        return load_colour_surface(fallback_colour, size)
    # Get Image location
    path = os.path.join(FOLDER_NAME, filename)
    try: # Attempt to load image + re-sizes it to block size
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)
    except (FileNotFoundError, pygame.error):
        print(f"Warning: Missing '{filename}'. Using colour.")
        return load_colour_surface(fallback_colour, size)
    
# --- Data Classes ---
@dataclass
class TowerType:
    """Stores the fixed statistics for a specific type of tower."""
    name: str
    cost: int
    range: int
    damage: int
    cooldown_frames: int
    color: tuple

    # Optional  Settings
    proj_speed: float = 5
    proj_size: int = 5

    # A list of map characters (e.g. 'T', 'B') that this tower can sit on.
    # By default, towers can only sit on 'T' (Grass), unless we specify otherwise.
    # We use a 'factory' here to give every tower its own fresh list.
    valid_tiles:list[str] = field(default_factory=lambda: ['T'])

    image_file:str|None = None

    @property
    def type(self): return self
    @property
    def ui_title(self): return self.name
    @property
    def ui_cost(self): return self.cost
    @property
    def ui_footer(self): return "(Click to Build)"
    @property
    def ui_cooldown(self): return self.cooldown_frames

@dataclass
class Info:
    text: str
    colour: tuple = TEXT
    padding: int = 0
    prev: str | None = None

# --- Game Data ---
LEVEL_MAP = [
    "TTTTTTTTTTTTTTTTTTTTTTTT",
    "TBTBTBTTBBTBTBBBTBTBTBTT",
    "TTTTTPPPPPPPPPPPBTBTTTTT",
    "TBTBTPTBTBTTBTBPBTBTBTBT",
    "TTTTTPTTTTTTTTTPTTTTTTTT",
    "PPPPPPBTBTBTBTBPBTBBBTBT",
    "TBTBTTTTTTTTTTTPTTTTTTTT",
    "TTTTTTTTTTTBTBTPBTBTBTBT",
    "TTTTTTTTTTTBTBTPBTBTBTBT",
    "TTTTTTTBTTBTBTBPBTBBBTBT",
    "TBTBTBTBTBTPPPPPTTTTTTTT",
    "TTTTTTTTTTTPBTBTBTBTBTBT",
    "TBTBTBTBTBTPTTTTTTTTTTTT",
    "TTTTTTTTTTTPBTBTBTBTBTBT",
    "TBTBTBTBTBTPTTTTTTTTTTTT",
    "TBTBTBTBTBTPTTTTTTTTTTTT",
    "TTTTTTTTTTTPBTBTBTBTBTBT",
    "TBTBTBTBTBTPTTTTTTTTTTTT",
    "TTTTTTTTTTTPBTBTBTBTBTBT",
    "TBTBTBTBTBTPTTTTTTTTTTTT",
    "TTTTTTTTTTTPPPPPPPPPPPPP",
    "TBTBTBTBTBTBTBTBTBTBTBTT",
    "TTTTTTTTTTTTTTTTTTTTTTTT",
    "TBTBTBTBTBTBTBTBTBTBTBTT",
    "TTTTTTTTTTTTTTTTTTTTTTTT",
]

TOWERS = {
    "Archer": TowerType(
        name="Archer Tower",
        cost=50,
        range=120,
        damage=10,
        cooldown_frames=45,
        color=(0, 0, 200),
        proj_speed=10,
        proj_size=4,
        image_file="Dog_1.png"
    ),
    "Cannon": TowerType(
        name="Cannon Tower",
        cost=150,
        range=80,
        damage=30,
        cooldown_frames=90, # Slower firing
        color=(150, 50, 0),
        proj_speed=5,        # Slower projectile
        proj_size=8,
        valid_tiles=['B']
    )
}

# --- Classes ---
class Timer:
    def __init__(self, duration:int, start_active=False):
        self.duration = duration
        self.current_time = 0 
        self.active = start_active
        if self.active:
            self.current_time = duration
    def update(self) -> bool:
        """ Ticks the timer down. Returns True if it JUST finished this frame. """
        if self.active:
            self.current_time -= 1
            if self.current_time <= 0:
                self.active = False
                return True # Finished this frame
        return False
    
    def activate(self):
        """ Resets and starts the timer """
        self.active = True
        self.current_time = self.duration
    def deactivate(self):
        """ Stops the timer completely """
        self.active = False
        self.current_time = 0

    def is_active(self) -> bool:    return self.active
    def get_progress(self) -> float:
        """ Returns a value between 0.0 (done) and 1.0 (just started) """
        if self.duration == 0: 
            return 0
        return self.current_time / self.duration

class Clickable:
    def __init__(self, rect:pygame.Rect):
        self.rect = rect
        self.is_selected = False
        self.is_hovered = False
    def update(self, mouse_pos:Pos):
        # Checks if mouse is hovering over it
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    def is_clicked(self, mouse_pos:Pos):
        # Returns True if the object was clicked
        return self.rect.collidepoint(mouse_pos)

class Button(Clickable):
    def __init__(self, x:int, y:int, size:int, tower_type:TowerType, font:pygame.font.Font, selected=False):
        rect = pygame.Rect(x, y, size, size)
        super().__init__(rect)
        self.type = tower_type
        self.font = font
        self.is_selected = selected
        self.image = load_image(tower_type.image_file, (size, size), tower_type.color)
        # Create Highlight 
        self.highlight_surf = load_colour_surface(HIGHLIGHT, (size, size))
        self.highlight_surf.set_alpha(100) # Make it transparent

    def draw(self, surface:Surf, current_money:int):
        # Draw Image 
        surface.blit(self.image, self.rect)
        # Draw Highlight on top (if hovered over) 
        if self.is_hovered:
            surface.blit(self.highlight_surf, self.rect)
        
        # Draw Selection Border
        if self.is_selected: # Thick Yellow Border
            pygame.draw.rect(surface, SELECTED, self.rect, 4)
        else: # Thin Black Border
            pygame.draw.rect(surface, UNSELECTED, self.rect, 2)

        # Draw Cost Text
        if current_money >= self.type.cost:
            price_color = AFFORDABLE
        else:
            price_color = EXPENSIVE

        text = self.font.render(f"${self.type.cost}", True, price_color)
        
        # Center the text below the button
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.bottom + 12))
        surface.blit(text, text_rect)

class Sprite(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, size: tuple[int,int]|int, image_name: str|None = None, colour = FALLBACK):
        if isinstance(size, int):
            size = (size, size)
        super().__init__()
        if image_name != "": # Load Image from File
            self.image = load_image(image_name, size, colour)
        elif colour: # Create Image from colour
            self.image = load_colour_surface(colour, size)
        else: # Error: Force Fallback Colour
            print("Missing a Sprite image or colour")
            self.image = load_colour_surface(FALLBACK, size)
        self.rect = self.image.get_rect(x=x, y=y)
        self.center_pos = Vector2(self.rect.center)
    def draw(self, screen:Surf):
        screen.blit(self.image, self.rect)
class Tile(Sprite):
    def __init__(self, col:int, row:int, type:str, BLOCK_SIZE:int, image_name="", colour:Colour=FALLBACK):
        self.col = col
        self.row = row
        self.type = type
        self.tower = None 
        super().__init__(col*BLOCK_SIZE, row*BLOCK_SIZE, BLOCK_SIZE, image_name, colour)
    def draw(self, screen:Surf):
        super().draw(screen)
        if GRID_LINES: # Optional Gridlines
            pygame.draw.rect(screen, (50, 50, 50), self.rect, 1)
    def can_place(self, tower_type:TowerType):
        if self.type not in tower_type.valid_tiles or \
            self.tower is not None:
            return False
        return True
class BaseTower(Sprite, Clickable):
    level: int
    type: TowerType
    cooldown_timer: Timer
    upgrade_msg: str = "(Click to Upg)"
    def __init__(self, col:int, row:int, block_size:int, colour:Colour, image_file:str|None = None):
        x = col * block_size
        y = row * block_size
        # Initialize Parent Classes (Sprite & Clickable)
        Sprite.__init__(self, x, y, block_size, image_file, colour)
        Clickable.__init__(self, self.rect)
    def update(self, mouse_pos:Pos):
        Clickable.update(self, mouse_pos)
    def draw_range(self, screen:Surf, colour = RANGE):
        radius = getattr(self, "range", 0)
        center = self.center_pos
        # Create rect around circle
        target_rect = pygame.Rect(
            center[0] - radius,  # X position
            center[1] - radius,  # Y position
            radius * 2,          # Width
            radius * 2           # Height
        )
        # Draw circle on transparent surface
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.circle(shape_surf, colour, (radius, radius), radius)
        screen.blit(shape_surf, target_rect)
    
    # @Property: For UI interaction
    @property
    def ui_title(self): 
        lvl = getattr(self, "level", 1)

        name = "Unknown Tower"
        if hasattr(self, "type"):
            name = self.type.name 
            
        return f"LVL {lvl} {name}"
    @property
    def ui_footer(self): 
        return self.upgrade_msg
    @property
    def ui_cooldown(self): 
        if hasattr(self, "cooldown_timer"):
            return self.cooldown_timer.duration
        return 0 
    @property
    def ui_cost(self):
        # Calls the student's get_upgrade_cost method
        if hasattr(self, "get_upgrade_cost"):
            return self.get_upgrade_cost() # type: ignore
        print("Create 'get_upgrade_cost' function")
        return 9999

class BaseSystem:
    INFO_RECT = pygame.Rect(10, 350, 180, 175)
    """ A parent class that enforces the structure for any major game component."""
    def __init__(self, x:int, y:int, width:int, height:int):
        self.font: pygame.font.Font = None # type: ignore
        self.rect = pygame.Rect(x, y, width, height)
        pass

    def is_clicked(self, pos:Pos): return self.rect.collidepoint(pos)
    def update(self): return True
    def draw(self, screen:Surf): pass
    def click(self, pos:Pos): pass

    def draw_text(self, screen:Surf, text:str, pos:Pos, colour:Colour=TEXT, center=False):
        """ Draws text relative to the System's position. 'pos' is a tuple (x, y) """
        if self.font is None: #Safety Check: Ensures Font exists
            print("Need to create a Font!")
            return
        
        # Render Text
        text_surface = self.font.render(str(text), True, colour)
        
        # Calculate position on screen (relative to BaseSystem's rect)
        pos = (self.rect.x + pos[0], self.rect.y + pos[1])

        if center: # Reposition on screen
            text_rect = text_surface.get_rect(center=pos)
        else:
            text_rect = text_surface.get_rect(topleft=pos)
        
        # Add text to screen
        screen.blit(text_surface, text_rect)

    def draw_rect(self, screen:Surf, rect:pygame.Rect|tuple, fill_colour:Colour|None=None, border_colour:Colour|None=None, border_width=0):
        """ Draw a rectangle relative to the system's position. """
        # Create a new rect, offset by the System's position
        target_rect = pygame.Rect(
            self.rect.x + rect[0],  # X offset
            self.rect.y + rect[1],  # Y offset
            rect[2],                # Width
            rect[3])                # Height
        
        # Draw Fill (Background)
        if fill_colour is not None:
            pygame.draw.rect(screen, fill_colour, target_rect)
            
        # Draw Border (Outline)
        if border_colour is not None and border_width > 0:
            pygame.draw.rect(screen, border_colour, target_rect, border_width)
    
    def draw_info_panel(self, screen:Surf, item, money:int):
        # Determine cost color
        if money >= item.ui_cost: 
            cost_col = AFFORDABLE 
        else: 
            cost_col = EXPENSIVE
        
        # Get Upgrade Previews (if they exist)
        info = {}
        if hasattr(item, "get_upgrade_stats"):
            info = item.get_upgrade_stats()
        
        # Build the Data List
        # .get() safely handles cases where keys don't exist: prevents crashing
        data = [
            Info(item.ui_title, item.type.color),
            Info(f"Dmg: {item.damage}", prev=info.get("damage")),
            Info(f"Rng: {item.range}",  prev=info.get("range")),
            Info(f"Cool: {item.ui_cooldown}", prev=info.get("cooldown")),
            Info(f"Cost: ${item.ui_cost}", cost_col, 10),
            Info(item.ui_footer, (150, 150, 150)) ]
        
        # Draw Background & Border
        self.draw_rect(screen, self.INFO_RECT, 
                       fill_colour=INFO_PANEL, 
                       border_colour=item.type.color, 
                       border_width=2)
        
        # Draw Text, line by Line 
        # We start drawing text slightly inside the box (+10 padding)
        current_y = self.INFO_RECT.y + 10 
        text_x = self.INFO_RECT.x + 10
        
        for line in data:
            # Access attributes using dot notation (.padding, .text, .color)
            # Add extra padding if the line asks for it
            current_y += line.padding

            #Draw Main Text
            self.draw_text(screen, line.text, (text_x, current_y), line.colour)
            
            # Draw Upgrade Previews (with Green Arrow)
            if line.prev:
                width, _ = self.font.size(str(line.text))
                
                # Draw the arrow and new value in Green
                self.draw_text(screen, f" -> {line.prev}", (text_x + width, current_y), UPGRADE)
            current_y += 25 # move down for next line
    def sort_path(self, path_coords: list[tuple[int,int]], 
        grid_cols: int, grid_rows: int, block_size: int
        ) -> list[Vector2]:
        """ Sorts the path Coordinates into a sequential list of Vectors. """
        if not path_coords: 
            print("Error: No path coordinates found!")
            return []
        
        # --- 1. FIND START NODE ---
        start_node = path_coords[0]
        for col, row in path_coords:
            # Now uses the variables passed in, not global ones
            if col == 0 or row == 0 or col == grid_cols - 1 or row == grid_rows - 1:
                start_node = (col, row)
                break

        # --- 2. SORTING LOGIC ---
        ordered_path = [start_node]
        unvisited = set(path_coords)
        unvisited.remove(start_node)
        
        current = start_node
        
        while unvisited:
            col, row = current
            neighbors = [
                (col, row - 1), (col, row + 1), 
                (col - 1, row), (col + 1, row)
            ]
            
            found_next = False
            for n in neighbors:
                if n in unvisited:
                    ordered_path.append(n)
                    unvisited.remove(n)
                    current = n
                    found_next = True
                    break
            
            if not found_next:
                print(f"Path broken at {current}")
                break

        # --- 3. CONVERT TO PIXELS ---
        offset = block_size // 2
        pixel_path = []
        
        for col, row in ordered_path:
            # Use the block_size passed into the function
            x = (col * block_size) + offset
            y = (row * block_size) + offset
            # We assume Vector2 is imported in TowerBase, or use pygame.math.Vector2
            pixel_path.append(pygame.math.Vector2(x, y))
            
        return pixel_path

