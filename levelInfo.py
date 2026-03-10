from NewBase import TowerType, UpgradeMult
MAP = [
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
        valid_tiles=['B'],
        upgrade_mults={
            UpgradeMult.COST: 1.0, 
            UpgradeMult.DAMAGE: 1.8, 
            UpgradeMult.RANGE: 1.0, 
            UpgradeMult.COOLDOWN: 0.95}
    ),
}
