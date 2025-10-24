from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pygame

from items import Item, create_item


@dataclass(slots=True)
class EnemyBlueprint:
    name: str
    stats: Dict[str, int]
    loot_table: List[Tuple[str, float]]
    experience: int


class Enemy:
    def __init__(self, enemy_id: str, blueprint: EnemyBlueprint, position: Tuple[int, int], tile_size: int) -> None:
        self.enemy_id = enemy_id
        self.name = blueprint.name
        self.stats = dict(blueprint.stats)
        self.max_health = self.stats.get("health", 30)
        self.stats["health"] = self.max_health
        self.rect = pygame.Rect(position[0], position[1], tile_size, tile_size)
        self.loot_table = blueprint.loot_table
        self.experience = blueprint.experience
        self.color = (200, 80, 80)

    def draw(self, surface) -> None:  # noqa: ANN001 - pygame surface
        pygame.draw.rect(surface, self.color, self.rect)

    def take_damage(self, amount: int) -> None:
        self.stats["health"] = max(self.stats["health"] - amount, 0)

    def is_alive(self) -> bool:
        return self.stats["health"] > 0

    def drop_loot(self) -> List[Item]:
        loot: List[Item] = []
        for item_id, chance in self.loot_table:
            if random.random() <= chance:
                item = create_item(item_id)
                if item:
                    loot.append(item)
        return loot


ENEMIES: Dict[str, EnemyBlueprint] = {
    "slime": EnemyBlueprint(
        name="Forest Slime",
        stats={"health": 30, "attack": 8, "defense": 1, "resistance": 0},
        loot_table=[("herb", 0.6)],
        experience=25,
    ),
    "goblin": EnemyBlueprint(
        name="Goblin Scout",
        stats={"health": 45, "attack": 12, "defense": 3, "resistance": 1},
        loot_table=[("iron_ore", 0.35), ("health_potion", 0.15)],
        experience=40,
    ),
    "wolf": EnemyBlueprint(
        name="Dire Wolf",
        stats={"health": 55, "attack": 15, "defense": 4, "resistance": 2},
        loot_table=[("herb", 0.2)],
        experience=50,
    ),
}


def create_enemy(enemy_id: str, position: Tuple[int, int], tile_size: int) -> Optional[Enemy]:
    blueprint = ENEMIES.get(enemy_id)
    if not blueprint:
        return None
    return Enemy(enemy_id, blueprint, position, tile_size)