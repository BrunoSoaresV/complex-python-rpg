from __future__ import annotations

from typing import Dict, List, Optional

import pygame

from items import Item, create_item, deserialise_item, resolve_item_id, serialise_item
from skills import ArcaneShield, Fireball, HealingLight


class Player:
    def __init__(self, spawn_pos: tuple[int, int], tile_size: int) -> None:
        self.tile_size = tile_size
        self.rect = pygame.Rect(spawn_pos[0], spawn_pos[1], tile_size, tile_size)
        self.color = (80, 170, 255)
        self.stats: Dict[str, int] = {
            "health": 100,
            "max_health": 100,
            "mana": 50,
            "max_mana": 50,
            "attack": 12,
            "defense": 5,
            "magic": 14,
            "resistance": 3,
            "level": 1,
            "experience": 0,
        }
        self.experience_to_next = 100
        self.inventory: List[Item] = [create_item("health_potion"), create_item("mana_potion")]
        self.inventory = [item for item in self.inventory if item]
        self.skills = [Fireball(), HealingLight(), ArcaneShield()]
        self.active_buffs: List[Dict[str, int]] = []
        self._cooldown_timer = 0.0

    def move(self, direction: str, world) -> None:  # noqa: ANN001 - world runtime type
        offsets = {
            "up": (0, -self.tile_size),
            "down": (0, self.tile_size),
            "left": (-self.tile_size, 0),
            "right": (self.tile_size, 0),
        }
        if direction not in offsets:
            return
        dx, dy = offsets[direction]
        proposed = self.rect.move(dx, dy)
        if world.is_walkable_rect(proposed):
            self.rect = proposed

    def update(self, delta_time: float) -> None:
        self._cooldown_timer += delta_time
        if self._cooldown_timer >= 1.5:
            self.restore_mana(1)
            self._cooldown_timer = 0.0

    def draw(self, surface) -> None:  # noqa: ANN001 - pygame surface
        pygame.draw.rect(surface, self.color, self.rect)

    def heal(self, amount: int) -> int:
        missing = self.stats["max_health"] - self.stats["health"]
        recovered = min(amount, missing)
        self.stats["health"] += recovered
        return recovered

    def restore_mana(self, amount: int) -> int:
        missing = self.stats["max_mana"] - self.stats["mana"]
        recovered = min(amount, missing)
        self.stats["mana"] += recovered
        return recovered

    def take_damage(self, amount: int) -> None:
        self.stats["health"] = max(self.stats["health"] - amount, 0)

    def is_alive(self) -> bool:
        return self.stats["health"] > 0

    def add_item(self, item: Item) -> None:
        if item:
            self.inventory.append(item)

    def remove_item_by_id(self, item_id: str) -> Optional[Item]:
        for index, item in enumerate(self.inventory):
            if resolve_item_id(item) == item_id:
                return self.inventory.pop(index)
        return None

    def consume_item(self, item_id: str) -> str:
        item = self.remove_item_by_id(item_id)
        if not item:
            return f"No {item_id.replace('_', ' ')} available."
        if not item.can_use():
            self.add_item(item)
            return "That item cannot be used right now."
        return item.apply(self)

    def list_inventory_ids(self) -> List[str]:
        return [resolve_item_id(item) for item in self.inventory]

    def add_temporary_buff(self, stat: str, amount: int, duration: int) -> None:
        self.stats[stat] += amount
        self.active_buffs.append({"stat": stat, "amount": amount, "remaining": duration})

    def tick_buffs(self) -> None:
        remaining_buffs: List[Dict[str, int]] = []
        for buff in self.active_buffs:
            buff["remaining"] -= 1
            if buff["remaining"] <= 0:
                self.stats[buff["stat"]] -= buff["amount"]
            else:
                remaining_buffs.append(buff)
        self.active_buffs = remaining_buffs

    def gain_experience(self, amount: int) -> None:
        self.stats["experience"] += amount
        while self.stats["experience"] >= self.experience_to_next:
            self.stats["experience"] -= self.experience_to_next
            self.level_up()

    def level_up(self) -> None:
        self.stats["level"] += 1
        self.stats["max_health"] += 12
        self.stats["max_mana"] += 6
        self.stats["attack"] += 3
        self.stats["defense"] += 2
        self.stats["magic"] += 3
        self.stats["resistance"] += 1
        self.stats["health"] = self.stats["max_health"]
        self.stats["mana"] = self.stats["max_mana"]
        self.experience_to_next = int(self.experience_to_next * 1.3)

    def to_dict(self) -> Dict:
        return {
            "position": [self.rect.x, self.rect.y],
            "stats": self.stats,
            "experience_to_next": self.experience_to_next,
            "inventory": [serialise_item(item) for item in self.inventory],
        }

    @classmethod
    def from_dict(cls, payload: Dict, tile_size: int) -> "Player":
        spawn = tuple(payload.get("position", (0, 0)))
        player = cls(spawn, tile_size)
        player.stats.update(payload.get("stats", {}))
        player.experience_to_next = payload.get("experience_to_next", 100)
        player.inventory.clear()
        for item_payload in payload.get("inventory", []):
            item = deserialise_item(item_payload)
            if item:
                player.add_item(item)
        return player