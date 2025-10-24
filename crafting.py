from __future__ import annotations

from collections import Counter
from typing import Dict

from items import create_item


class CraftingSystem:
    def __init__(self):
        self.recipes: Dict[str, Dict[str, int]] = {
            "health_potion": {"herb": 2},
            "mana_potion": {"herb": 1, "iron_ore": 1},
        }

    def craft(self, player, item_name: str) -> str:
        if item_name not in self.recipes:
            return "Unknown recipe."
        if not self.has_ingredients(player, item_name):
            return "Missing required ingredients."

        self.remove_ingredients(player, item_name)
        crafted = create_item(item_name)
        if crafted:
            player.add_item(crafted)
            return f"Crafted {crafted.name}."
        return "Recipe failed to produce an item."

    def has_ingredients(self, player, item_name: str) -> bool:
        required = self.recipes[item_name]
        inventory_counts = Counter(player.list_inventory_ids())
        return all(inventory_counts.get(resource, 0) >= amount for resource, amount in required.items())

    def remove_ingredients(self, player, item_name: str) -> None:
        required = Counter(self.recipes[item_name])
        for resource_id in list(required.elements()):
            player.remove_item_by_id(resource_id)