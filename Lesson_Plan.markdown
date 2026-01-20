# Teacher's Lesson Plan: Tower Defence in Python

**Repository:** [https://github.com/FlamboyantKiwi/Tower-Defence](https://github.com/FlamboyantKiwi/Tower-Defence)

**Prerequisite:** Students must have the `TowerBase.py` file and the `Assets` folder in their project directory before starting.

**Core Concept:** This course simulates using a "Game Engine" or "API." Students don't write the low-level utility code (timers, rendering sprites); they write the **Game Logic** that controls those utilities.

### A Note on Imports:
This lesson plan explicitly lists the specific classes and functions used in each lesson (e.g., `from TowerBase import Tile`). This is to help you, the teacher, track exactly which tools are being introduced. 

**However**, for students, I recommend simply using:`from TowerBase import *`
This imports the entire library at once, allowing students to focus on writing game logic without worrying about "Import Errors" every time they use a new class.


## Phase 1: The World (Setup)
*Building the foundation using the provided library.*

### Lesson 1: The Window & Loop
* **Goal:** Initialize the game window using Pygame, define the configuration constants, and establish the main game loop.
* **From TowerBase:** (None required yet, but the file must be present).
* **Student Code:**
    * **Configuration:** Define `MAP_WIDTH`, `BLOCK_SIZE`, and RGB Color constants.
    * **Initialization:** Call `pygame.init()` and create the window using `display.set_mode`.
    * **The Loop:** Write the `while playing:` loop with `clock.tick(FPS)` and `pygame.event.get()` to handle closing the window.
    * **Math Helper:** Implement `get_tile_coords(pos)` to handle the conversion from Pixel Coordinates to Grid Coordinates (using integer division `//`).

### Lesson 2: The Map & Manager
* **Goal:** Create the `GameManager`, pass the level data to render the grid, and calculate the enemy path.
* **Specific Tools Used:** `UIManager` (Parent class), `Tile` (Class), `LEVEL_MAP` (Data), `sort_path` (Function).
* **Student Code:**
    * **GameManager:** Create the class (inheriting from `UIManager`) and move the logic variables (`money`, `lives`) inside.
    * **Grid Logic (`setup_map`):** 
        * Iterate through `LEVEL_MAP` using `enumerate`. 
        * Check the character ('T', 'P', 'B') to set the color.
        * Instantiate `Tile` objects and append them to `self.grid`.
    * **Path Logic:** 
        * While iterating, identify 'P' tiles and add their **Grid Coordinates** (col, row) to a list.
        * Call `sort_path()` at the end of the function to generate the ordered waypoint list (`self.path`).
        * **Important Note:** `sort_path` returns a list of **Vectors in Pixel Coordinates** (the center of the tile), *not* Grid Coordinates. This prepares the data for the Enemy movement in Lesson 4.
    * **Main Loop Update:** Instantiate `game_manager`, add it to a `sections` list, and iterate through that list to call `.draw()`.

### Lesson 3: The Update Loop & Interaction
* **Goal:** Enable user interaction (clicking the grid) and finalize the Game Loop structure.
* **Specific Tools Used:** `pygame.MOUSEBUTTONDOWN`, `UIManager.is_clicked` (Inherited).
* **Student Code:**
    * **Click Logic (`click`):**
        * Implement the `click` method in `GameManager`.
        * Use `get_tile_coords(pos)` to convert the mouse pixel position into Grid Coordinates.
        * Add a `print()` statement to verify clicks are being detected in the console.
    * **Main Loop - Input Handling:**
        * Update the event loop to check for `pygame.MOUSEBUTTONDOWN`.
        * Iterate through the `sections` list.
        * Use `ui.is_clicked(event.pos)` to check if the click happened inside that UI element (The Map).
        * If true, call `ui.click(event.pos)`.
    * **Main Loop - Updates:**
        * Add the `if playing:` block to call `game_manager.update()`.
        * Ensure `update()` returns a boolean (True = Keep Playing, False = Game Over) so the loop can be broken later.

---

## Phase 2: The Enemy (AI & Movement)
*Writing custom logic for Enemy entities.*

### Lesson 4: Creating an Enemy
* **Goal:** Define the Enemy entity, manage it with a Sprite Group, and spawn it at the start of the path using a debug key.
* **Specific Tools Used:** `Sprite` (Parent class), `Vector2` (for position handling), `pygame.sprite.Group`.
* **Student Code:**
    * **Configuration:** Define `ENEMY_HP`, `ENEMY_SPEED`, etc.
    * **GameManager Updates:**
        * Initialize `self.enemies = pygame.sprite.Group()`.
        * Implement `create_enemy(hp, speed, bounty)`: Instantiate an Enemy and add it to the group.
        * Update `draw()`: Call `self.enemies.draw(screen)`.
    * **Enemy Class:**
        * Define `class Enemy(Sprite)`.
        * Implement `__init__`:
            * Set `self.path` and `self.path_index`.
            * Set initial position (`self.pos`) to the first coordinate in `path`.
            * Align the sprite `rect.center` to the position.
    * **Input Testing:**
        * Add `pygame.KEYDOWN` check for `K_SPACE` in the main loop to trigger `game_manager.create_enemy()`.

### Lesson 5: Moving Enemies
* **Goal:** Implement the physics loop to make enemies follow the path waypoints.
* **Specific Tools Used:** `Vector2` methods (`normalize`, `length`).
* **Student Code:**
    * **Enemy Update Logic (`Enemy.update`):**
        * Calculate the vector to the next target node (`target - current`).
        * **Distance Check:** If distance > speed, move towards target.
        * **Node Switching:** If close enough, snap to the node and increment `self.target_node` to aim for the next one.
        * **Breach Flag:** Set `self.breached = True` if the enemy runs out of path nodes.
    * **Game Loop Updates (`GameManager.update`):**
        * Iterate through the `self.enemies` sprite group.
        * Call `enemy.update()`.
        * **Cleanup:** Check if an enemy has `breached`. If so, `remove()` it from the group and subtract a life.

### Lesson 6: Constant Enemies (Automation)
* **Goal:** Create an infinite stream of enemies that spawn at regular intervals (without debug keys)
* **Specific Tools Used:** `Timer` (Class), `SPAWN_DELAY` (Constant).
* **Student Code:**
    * **The Spawner Class:**
        * Define `class EnemySpawner`.
        * Initialize `self.spawn_timer` with `SPAWN_DELAY`.
        * Implement `update()`:
            * Check `if self.spawn_timer.update():`.
            * If true, call `spawn_enemy()` and `activate()` the timer again.
    * **Integration:**
        * Add `self.spawner = EnemySpawner(self)` to `GameManager`.
        * Call `self.spawner.update()` in the main game loop.

### Lesson 7: Waves & Difficulty
* **Goal:** Implement a full Wave System with breaks, distinct waves, and increasing difficulty.
* **Specific Tools Used:** `Timer` (Class).
* **Student Code:**
    * **Configuration:** Add constants for `WAVES_BREAK`, `STARTING_ENEMIES`, `ENEMIES_PER_WAVE`, etc.
    * **State Machine (`EnemySpawner`):** 
        * Refactor the simple update loop into 3 distinct states:
            * `"COUNTDOWN"`: Tick the `wave_timer`. When done, call `start_new_wave()`.
            * `"SPAWNING"`: Use the timer logic from Lesson 6, but decrement `enemies_to_spawn`. When 0, switch to `"WAITING"`.
            * `"WAITING"`: Check `if len(manager.enemies) == 0`. If true, reset to `"COUNTDOWN"`.
    * **Wave Logic (`start_new_wave`):**
        * Increment `wave_number`.
        * Calculate `enemies_to_spawn` using the linear formula: `STARTING + (WAVE * PER_WAVE)`.
    * **Difficulty Scaling (`spawn_enemy`):**
        * Modify the create call to increase HP, Speed, and Bounty based on the current `wave_number`.
        * **Important Note:**  This is a great opportunity for students to be creative. They can decide which variables to increase and by how much (e.g., fast weak enemies vs slow tanky enemies).

---

## Phase 3: The Defense (Interaction)
*Connecting user input to game objects.*

### Lesson 8: Placing Towers
* **Goal:** Enable the player to spend money to place towers on valid tiles.
* **Specific Tools Used:** `BaseTower` (Parent class), `TowerType` (Data), `TOWERS` (Data).
* **Student Code:**
    * **The Tower Class:**
        * Define `class Tower(BaseTower)`.
        * **Init:** Copy stats (`range`, `damage`, `cooldown`) from the `TowerType` to the instance.
        * **Draw:** Draw the tower image. *Bonus:* Check `if self.is_hovered:` to call `self.draw_range(screen)`.
    * **Economy Logic (`GameManager`):**
        * Initialize `self.towers = pygame.sprite.Group()`.
        * Implement `attempt_buy(cost)`: Check if `self.money >= cost`. If yes, subtract and return True.
    * **Placement Logic (`click`):**
        * Update the click handler:
            * Get the specific `Tile` clicked.
            * Check `if tile.can_place(selected_type):`.
            * Call `attempt_buy`.
            * If successful, instantiate `Tower`, add to sprite group, and link it (`tile.tower = new_tower`).
    * **Testing:** Try to place towers on Grass vs Path vs Rock. Verify money goes down.

### Lesson 9: The Upgrader (Economy)
* **Goal:** Allow players to upgrade existing towers to increase their stats.
* **Specific Tools Used:** `TowerType` (Data).
* **Student Code:**
    * **Tower Class Updates:**
        * Implement `get_upgrade_cost()`: Calculate cost based on level (e.g., `base_cost * level * 0.7`).
        * Implement specific stat helpers:
            * `get_upgraded_damage()`: Return `damage * 1.5`.
            * `get_upgraded_range()`: Return `range + 15`.
            * `get_upgraded_cooldown()`: Return `duration * 0.9` (faster firing).
        * Implement `upgrade()`: Call these helpers to update `self.damage`, `self.range`, and `self.cooldown_timer.duration`, then increment `self.level`.
    * **GameManager Updates (`click`):**
        * Modify the `click` logic to handle two scenarios:
            1.  **Empty Tile:** Build a new tower (Lesson 8 logic).
            2.  **Occupied Tile:** Call `tower.get_upgrade_cost()`. If affordable, call `tower.upgrade()`.
    * **Testing:** Build a tower, click it again, and watch the console print "Upgraded to Level 2."

---

## Phase 4: Physics (Combat)
*The math behind shooting and collisions.*

### Lesson 10: Projectiles & Targeting
* **Goal:** Make towers identify the best target and fire visual projectiles at them.
* **Specific Tools Used:** `Sprite` (Parent class), `Vector2` (methods: `angle_to`, `rotate`, `distance_to`).
* **Student Code:**
    * **Projectile Class:**
        * Define `class Projectile(Sprite)`.
        * **Velocity Math:** Create a right-facing vector `Vector2(speed, 0)` and `rotate(-angle)` to match the target direction.
        * Implement `update()`: Move the position by velocity every frame.
    * **Tower Targeting (`find_target`):**
        * Iterate through `game_manager.enemies`.
        * **Range Check:** Use `self.center_pos.distance_to(enemy.rect.center)`.
        * **Priority:** Keep track of the enemy with the highest `path_index` (closest to the exit).
    * **Tower Firing (`fire`):**
        * Calculate the direction vector: `target_pos - self.center_pos`.
        * **Angle Math:** Use `direction.angle_to(Vector2(1, 0))` to find the rotation angle needed.
        * Instantiate `Projectile` and add it to `self.projectiles`.
    * **Tower Update:**
        * Update the `cooldown_timer`.
        * If active, find a target and fire.

### Lesson 11: Collision & Damage
* **Goal:** Detect when bullets hit enemies, apply damage, and handle rewards.
* **Specific Tools Used:** `pygame.sprite.groupcollide` (The magic function that checks collisions between two lists).
* **Student Code:**
    * **Enemy Logic (`hit`):**
        * Implement `hit(damage)`: Subtract damage from health. Return `True` if health <= 0 (Dead), else `False`.
    * **Projectile Logic (Cleanup):**
        * Update `Projectile.update()`: Check `distance_to(start_pos)`. If it exceeds `range_limit`, call `self.kill()` to delete the sprite so the game doesn't slow down.
    * **Combat Logic (`Tower.update`):**
        * Call `pygame.sprite.groupcollide(enemies, self.projectiles, False, True)`.
        * *Note:* The `True` argument automatically deletes the projectile upon impact.
        * **Damage Loop:** Iterate through the collision dictionary.
        * Sum up the damage of all projectiles hitting that specific enemy.
        * Call `enemy.hit(total_damage)`.
        * **Death Handler:** If `hit` returns True, remove the enemy from the game group and add `enemy.bounty` to `game_manager.money`.

---

## Phase 5: The Interface (UI/UX)
*Polishing the user experience using the Library's UI tools.*

### Lesson 12: Visual HUD
* **Goal:** Create a sidebar interface to display money, lives, and tower purchase buttons.
* **Specific Tools Used:** `Button` (Class), `UI_WIDTH` (Constant), `TOWERS` (Data).
* **Student Code:**
    * **Configuration:** Add UI constants (`UI_BTN_SIZE`, `UI_GAP`, `UI_START_Y`).
    * **Interface Class Setup:**
        * Define `class Interface(UIManager)`.
        * **Init:** Initialize with `super().__init__(MAP_WIDTH, 0, UI_WIDTH, MAP_HEIGHT)` (placing it to the right of the map).
        * **Button Creation (`create_buttons`):**
            * Iterate through `TOWERS.values()`.
            * Calculate grid positions (col/row) and pixel positions (x/y) for a 2-column layout.
            * Instantiate `Button` objects and store them in `self.buttons`.
    * **Drawing (`draw`):**
        * Draw the sidebar background rectangle.
        * Use `self.draw_text()` to display Money and Lives.
        * Iterate through `self.buttons` and call `btn.draw(screen, money)`.
    * **Integration:**
        * Instantiate `Interface` in the main loop.
        * Add it to the `sections` list so it gets drawn.
        
### Lesson 13: UI Interaction
* **Goal:** Enable button clicking, selection highlighting, and the pop-up Info Panel.
* **Specific Tools Used:** `UIManager.draw_info_panel` (Inherited method), `GameManager` (Reference).
* **Student Code:**
    * **Manager Helpers:**
        * Implement `get_hovered()`: Loop through towers to return the specific instance under the mouse.
        * Implement `is_selected(type)`: Return True if the passed type matches `self.selected_type`.
        * Implement `get_wave_info()`: Bridge function to get text from the Spawner.
    * **Interface Updates:**
        * **Update Loop:** Add `btn.update(mouse_pos)` to `Interface.update` so buttons know when they are hovered.
        * **Click Logic:** Update `Interface.click()`:
            * Check `if btn.is_clicked(pos):`.
            * Update Game State: `self.manager.selected_type = btn.type`.
            * Update Visuals: Loop through all buttons to set `is_selected = False`, then set the clicked one to `True`.
        * **Info Panel Logic (`draw`):**
            * Determine `item_to_draw`: Use the logic `hovered_tower or selected_type`.
            * Call `self.draw_info_panel(screen, item, money)`.
        * **Wave Info:** Draw the `wave_message` text at the bottom of the sidebar.
---

## Phase 6: Content (Polish)
*Turning a tech demo into a real game: Optional Improvements and Personal Touches*

### Lesson 14: Customization & Expansion
* **Goal:** Replace placeholder shapes with images, design a custom level, and create unique tower types.
* **Specific Tools Used:** `TowerType` (Data Class), `TOWERS.update()` (Dictionary method), `image_name` (Sprite argument).

#### 1. Visual Polish (Sprites)
* **Concept:** The `TowerBase` library handles image loading automatically if you provide a filename.
* **Student Code:**
    * **Enemy Class:** Update `super().__init__` to include `image_name="Bug_1.png"`.
    * **Tower Class:** Update `super().__init__` to pass `tower_type.image_file`.
    * **Tower Data:** Add `image_file="Tower_1.png"` to the `TowerType` definitions in the `TOWERS` dictionary.
    * *Note:* Ensure students have an `Assets` folder with these PNG files.

#### 2. Level Design
* **Concept:** The map is just a list of strings. Changing the strings changes the world.
* **Student Code:**
    * Create a new list variable `New_Level` (List of Strings).
    * Design a winding path using 'P' (Path), 'T' (Grass), and 'B' (Obstacles).
    * **Constraint:** Ensure the path is continuous (no gaps) from left to right!
    * **Initialization:** Update the game start: `game_manager = GameManager(New_Level)`.

#### 3. New Tower Types
* **Concept:** Creating new gameplay styles by manipulating data, not just code.
* **Student Code:**
    * Define a new dictionary `new_towers`.
    * **The Sniper:** High Range (200), High Damage (100), Slow Cooldown (300).
    * **The Machine Gun:** Low Range (90), Low Damage (4), Fast Cooldown (8).
    * **Merge:** Use `TOWERS.update(new_towers)` to add these to the game. The UI will automatically resize to fit the new buttons (thanks to Lesson 12's grid math!).

#### 4. Balancing & Tweakable Variables
* **Activity:** Now that the game is complete, give students time to "break" and "fix" the balance.
* **Things they can change:**
    * **Economy:** `STARTING_MONEY`, `ENEMY_BOUNTY`.
    * **Difficulty:** `ENEMY_HP_INCREASE` (make waves scale faster).
    * **Pacing:** `SPAWN_DELAY` (make enemies rush in faster).
    * **Visuals:** `proj_color` and `proj_size` (make the Sniper shoot giant purple lasers).

#### 5. Optional Extension: Game Restart Logic
* **Concept:** Instead of the window closing when lives hit 0, we can reset the objects to start fresh.
* **Student Code:**
    * Modify the main `while playing:` loop to capture the result of `update()`.
    * If `game_active` is False, instantiate a new `GameManager` and reconnect the interface.

### Final Review
* **Check:** Does the game loop end correctly after Game Over?
* **Check:** Do the new towers have distinctive strengths and weaknesses?
* **Check:** Is the new map clear to read?