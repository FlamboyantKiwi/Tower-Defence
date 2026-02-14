import pygame, os
from dataclasses import dataclass, field

Vector2 = pygame.math.Vector2
Colour = tuple[int,int,int]
Pos = tuple[int|float, int|float] | Vector2

FOLDER_NAME = "Assets" 
FALLBACK = (255, 0, 255) # Hot Pink
AFFORDABLE = (0, 255, 0) # Green
EXPENSIVE = (255, 100, 100) # Red
SELECTED = (255, 255, 0) # Yellow
UNSELECTED = (0,0,0) # Black
HIGHLIGHT = (255, 255, 255) # WHITE
TEXT = (255,255,255)
UPGRADE = (0,255,0)

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
    
def create_solid_surface(colour: Colour, size: tuple[int, int], alpha=255) -> pygame.Surface:
    """Creates a plain colored square."""
    surf = pygame.Surface(size)
    surf.fill(colour)
    surf.set_alpha(alpha)
    return surf

def load_surface(size: tuple[int, int], filename: str|None = None, colour: Colour|None = None) -> pygame.Surface:
    """ Attempts to load an image. 
    If that fails (or filename is None), it tries the specific 'colour'.
    If that is None, it defaults to the global FALLBACK_COLOUR. """
    # Attempt to load Image
    if filename:
        path = os.path.join(FOLDER_NAME, filename)
        try:
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, size)
        except (FileNotFoundError, pygame.error) as e:
            print(f"Warning: Could not load '{filename}' ({e}). Falling back to colour.")

    # Attempt to use specific Colour (if image failed or wasn't requested)
    if colour:
        return create_solid_surface(colour, size)

    # Absolute Fallback (if no image and no colour provided)
    print("Error: No valid image or colour provided. Using global fallback.")
    return create_solid_surface(FALLBACK, size)

def get_center(vector:Vector2):
    return (int(vector.x), int(vector.y))

def get_grid_pos(index:int, cols:int=2, start:Pos=(10, 130), size:Pos=(50, 50), gap:Pos=(10, 10)):
        """ Calculates the top-left (x, y) for an item in a grid.
        Args:
            index (int): The item number (0, 1, 2...)
            cols (int):  How many items before wrapping to the next row?
            start (tuple): (x, y) pixel coordinates of the top-left corner.
            size (tuple):  (width, height) of the item itself.
            gap (tuple):   (x_gap, y_gap) space between items.
        """
        # 1. Logic: Convert linear index (0,1,2,3) to Grid (col, row)
        current_col = index % cols  
        current_row = index // cols 

        # 2. Math: Calculate pixel position
        # Position = Start + (Which Column * (Item Width + Gap Width))
        x = start[0] + (current_col * (size[0] + gap[0]))
        y = start[1] + (current_row * (size[1] + gap[1]))
        
        return x, y

def sort_path(path_coords: list[tuple[int,int]], 
    grid_cols: int, grid_rows: int, block_size: int) -> list[Vector2]:
    """ Sorts the path Coordinates into a sequential list of Vectors. """
    if not path_coords: 
        print("Error: No path coordinates found!")
        return []
    
    # Find Start Node
    start_node = path_coords[0]
    for col, row in path_coords:
        # Now uses the variables passed in, not global ones
        if col == 0 or row == 0 or col == grid_cols - 1 or row == grid_rows - 1:
            start_node = (col, row)
            break

    # Start Sorting
    ordered_path = [start_node]
    unvisited = set(path_coords)
    if start_node in unvisited:
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

    # Convert from tile coords to pixel coords
    offset = block_size // 2
    pixel_path = []
    
    for col, row in ordered_path:
        # Use the block_size passed into the function
        x = (col * block_size) + offset
        y = (row * block_size) + offset
        # We assume Vector2 is imported in TowerBase, or use pygame.math.Vector2
        pixel_path.append(pygame.math.Vector2(x, y))
        
    return pixel_path

@dataclass
class Info:
    text: str
    next_value: str | int | None = None # The green "upgrade" number
    colour: tuple = (255, 255, 255)     # Default White
    padding: int = 0

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
    proj_image_file = None
    proj_speed: float = 5
    proj_size: int = 5

    # Factory prevents all towers sharing the same list in memory
    valid_tiles:list[str] = field(default_factory=lambda: ['T'])

    image_file:str|None = None

    def get_ui_details(self) -> list[Info]:
        return [
            Info(self.name, colour=self.color),
            Info(f"Dmg: {self.damage}"),
            Info(f"Rng: {self.range}"),
            Info(f"Cool: {self.cooldown_frames}"),
            Info(f"Cost: ${self.cost}", colour=(255, 215, 0), padding=10), # Gold color
            Info("(Click to Build)", colour=(150, 150, 150))
        ]

    def can_afford(self, current_money: int) -> bool:
        """ Returns True if the player has enough money for the next upgrade. """
        return current_money >= self.cost

class Button(Clickable):
    def __init__(self, x:int, y:int, size:int, tower_type:TowerType, font:pygame.font.Font, selected=False):
        rect = pygame.Rect(x, y, size, size)
        super().__init__(rect)
        self.type = tower_type
        self.font = font
        self.is_selected = selected
        self.image = load_surface((size, size), tower_type.image_file, tower_type.color)
        #ensure image is in center of button
        self.icon_rect = self.image.get_rect(center=self.rect.center)
        # Create Highlight 
        self.highlight_surf = create_solid_surface(HIGHLIGHT, (size, size), alpha=100)


    def draw(self, surface:pygame.Surface, current_money:int):
        # Draw Image 
        surface.blit(self.image, self.icon_rect)
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

        draw_text(surface, f"${self.type.cost}", 
                 (self.rect.centerx, self.rect.bottom + 12), 
                 self.font, price_color, center=True)

    @classmethod
    def create_grid(cls, towers:dict, start_x:int, start_y:int, cols:int, size:int, gap:tuple[int,int], font:pygame.font.Font) -> list["Button"]:
        """  Takes a list of TowerTypes and returns a list of Button objects 
        arranged in a grid. """
        buttons = []
        
        for i, t_type in enumerate(towers.values()):
            # Grid Math (Row and Column)
            col = i % cols
            row = i // cols
            
            # Pixel Math (Position on screen)
            x = start_x + (col * (size + gap[0]))
            y = start_y + (row * (size + gap[1]))
            
            # Create the Button 
            # 'cls' is a reference to the Button class itself
            new_btn = cls(x, y, size, t_type, font)
            buttons.append(new_btn)
        return buttons

def draw_text(screen, text, pos, font, colour=TEXT, center=False):
    """ Helper to render text to the screen. """
    surf = font.render(str(text), True, colour)
    if center:
        rect = surf.get_rect(center=pos)  
    else:
        rect = surf.get_rect(topleft=pos)
    screen.blit(surf, rect)

def draw_list(screen:pygame.Surface, data_list:list[Info]|list[str], start_pos:Pos, font, colour=TEXT, line_height=25):
    """ Draws a vertical list of text. Converts strings to Info objects automatically. """
    start_x, start_y = start_pos
    
    for i, item in enumerate(data_list):
        # Skip if line is empty
        if item == "":
            continue

        # Normalize Data
        if isinstance(item, str):
            item = Info(text=item, colour=colour)

        # Calculate Position (Using the Grid helper)
        x, y = get_grid_pos(i, cols=1, start=(start_x, start_y), size=(0, line_height), gap=(0,0))
        y += item.padding

        # Draw
        draw_text(screen, item.text, (x, y), font, item.colour)

        if item.next_value:
            # FIX: Use 'font', not 'self.font'
            text_width = font.size(item.text)[0]
            draw_text(screen, f"-> {item.next_value}", (x + text_width + 5, y), font, UPGRADE)

def get_local_pos(global_mouse_pos, global_rect):
        """ Converts a screen position (610, 50) to a UI position (10, 50) """
        return (global_mouse_pos[0] - global_rect.x, 
                global_mouse_pos[1] - global_rect.y)
