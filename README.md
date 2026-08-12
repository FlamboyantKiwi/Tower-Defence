# Modular 2D Tower Defense Game

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-green.svg)

A feature-rich, modular 2D Tower Defense game built from scratch in Python using Pygame. Designed specifically as an educational template or student project, the codebase is cleanly separated into distinct modules to make teaching, extending, and customizing game mechanics straightforward.

---

## 🚀 Core Architecture & Features

* **Modular Component Design:** Cleanly separated code architecture (`base.py`, `sprites.py`, `levelInfo.py`, and the main execution script) allows students to focus on individual game systems without friction.
* **Data-Driven Tower System:** New towers (such as the Archer, Cannon, or Gold Farm) can be effortlessly created, balanced, and customized inside `levelInfo.py` using simple configuration data classes (`TowerType`).
* **Grid-Based Mapping & Pathfinding:** Maps are initialized via text-based arrays (`MAP`), where path coordinates are automatically scanned, sorted, and converted into sequential vector nodes for enemy traversal.
* **Dynamic Upgrade Multipliers:** Towers support leveling mechanics governed by automated scaling multipliers (`UpgradeMult`) that adjust costs, damages, ranges, and firing speeds per level.
* **Automated Wave Progression:** A built-in `Spawner` handles wave breaks, countdown timers, and progressive difficulty scaling for enemy health, movement speed, and gold bounties.
* **Interactive UI Sidebar:** Features a grid selection menu for tower purchasing, live tracking of player money and lives, and a context-sensitive info panel displaying live stats and upgrade details.

---


## 📂 Project Structure

```text
Tower-Defence/
├── main.py           # Main execution loop, GameManager, and UI rendering
├── base.py           # Core data classes, UI elements, timers, and pathfinding math
├── sprites.py        # Entity logic for Tiles, Towers, Projectiles, and Enemies
├── levelInfo.py      # Level layouts, paths, tile color mappings, and tower definitions
└── Assets/           # Sprites and graphical assets for entities and items
```


## 🛠️ Getting Started

### Prerequisites
You only need Python 3 installed. The only external dependency is Pygame.

```bash
pip install pygame
```

### Running the Game

1. Clone the repository:
```bash
git clone https://github.com/FlamboyantKiwi/Tower-Defence.git
```
2. Navigate to the directory:
```bash
cd Tower-Defence
```
3. Run the main executable:
```bash
python main.py
```

## ⌨️ Controls & Gameplay
* **Left-Click:** Select a tower blueprint from the sidebar, place a tower on valid grid tiles, or click existing towers to inspect and upgrade them.

* **Objective:** Manage your starting resources ($500 money, 20 lives) to prevent incoming waves of enemies from reaching the end of the path.

---
<div align="center">
  <small>Created by <b>Freddy Edmunds</b> | <a href="https://github.com/FlamboyantKiwi">GitHub</a> | <a href="https://freddyedmunds.co.uk">freddyedmunds.co.uk</a></small>
</div>