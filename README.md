# Complex Python RPG

Embark on a lightweight top-down adventure powered by Pygame. Guide the hero through a handcrafted map, complete quests for the locals, battle monsters in a turn-based arena, and gather resources to craft useful potions.

## Key Features
- **Exploration**: Move on a tile-based world, talk to NPCs, and harvest resources.
- **Combat**: Turn-based encounters with skills, consumables, and enemy loot tables.
- **Progression**: Level up, learn skills, and earn rewards from quests.
- **Crafting**: Convert gathered materials into helpful consumables.
- **Persistence**: Save and load your adventure at any time.

## Controls
- Arrow Keys: Move the player.
- `E`: Interact with NPCs or harvest resources.
- `1` / `2` / `3`: Combat actions (basic attack, Fireball, Healing Light).
- `4` / `5`: Use health or mana potion in combat.
- `6`: Cast Arcane Shield in combat.
- `I`: Open inventory (use consumables with `Enter`).
- `C`: Open crafting menu.
- `S`: Save game.
- `L`: Load game.
- `Esc`: Exit current menu or flee combat (returns to camp).

## Running the Game
```bash
python main.py
```

Ensure Pygame is installed (`pip install pygame`). The game targets a 1280x720 window and runs at 60 FPS.