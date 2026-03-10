from base import TowerType, UpgradeMult, FALLBACK

MAP = [
    "111111111111111111111111",
    "121212112212122212121211",
    "111110000000000021211111",
    "121210121211121012121212",
    "111110111111111011111111",
    "000000212121212021222121",
    "121211111111111011111111",
    "111111111112121012121212",
    "111111111112121012121212",
    "111111121112121012122212",
    "121212121210000011111111",
    "111111111110212121212121",
    "121212121210111111111111",
    "111111111110212121212121",
    "121212121210111111111111",
    "121212121210111111111111",
    "111111111110212121212121",
    "121212121210111111111111",
    "111111111110212121212121",
    "121212121210111111111111",
    "111111111110000000000000",
    "121212121212121212121211",
    "111111111111111111111111",
    "121212121212121212121211",
    "111111111111111111111111"]
PATH = "0"
TILE_COLORS = {
    PATH: "#C2B280", # Path (Sand)
    "1": "#228B22", # Grass
    "2": "#646464", # Base/Block
    " ": FALLBACK  # Error colour
}

def get_colour(i:str|int):
    return TILE_COLORS.get(str(i), FALLBACK)

TOWERS = {
    "Archer": TowerType(
        name="Archer Tower",
        cost=50,
        range=120,
        damage=10,
        cooldown_frames=45,
        color="#5cb3ff",
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
        color="#963200",
        proj_speed=5,        # Slower projectile
        proj_size=8,
        valid_tiles=['2'],
        upgrade_mults={
            UpgradeMult.COST: 1.0, 
            UpgradeMult.DAMAGE: 1.8, 
            UpgradeMult.RANGE: 1.0, 
            UpgradeMult.COOLDOWN: 0.95}
    ),
    "Farm": TowerType(
        name="Gold Farm",
        cost=20,
        range=0,             # Doesn't need range
        damage=25,           # This is now the income amount
        cooldown_frames=180, # Generates money every 3 seconds (60fps * 3)
        color=(255, 215, 0), # Gold color
        valid_tiles=['1', '2'], # Can place on grass or base
        upgrade_mults={
            UpgradeMult.COST: 2, 
            UpgradeMult.DAMAGE: 1.5,   # Income increases by 50% per level
            UpgradeMult.RANGE: 1.0, 
            UpgradeMult.COOLDOWN: 0.95 # Gets slightly faster
        },
        is_farm = True
    )
}
