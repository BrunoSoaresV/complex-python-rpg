from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

import pygame

from dialogue import DialogueNode, DialogueOption, DialogueTree
from enemies import Enemy, create_enemy
from items import create_item
from npcs import NPC
from quests import Quest


TILE_COLOURS = {
    "#": (40, 40, 40),
    ".": (60, 110, 60),
    "T": (34, 139, 34),
    "W": (30, 70, 130),
}


MAP_TEMPLATE: List[str] = [
    "########################",
    "#....E......T......E..#",
    "#..####..N.......###..#",
    "#..#..#............#..#",
    "#..#..#....P.......#..#",
    "#..#..######..T....#..#",
    "#..#...............#..#",
    "#..#######..E...N..#..#",
    "#.....................#",
    "########################",
]


class World:
    def __init__(self) -> None:
        self.tile_size = 48
        self.map_data = MAP_TEMPLATE
        self.width = len(self.map_data[0])
        self.height = len(self.map_data)
        self.spawn_point = (self.tile_size * 3, self.tile_size * 4)
        self.enemies: List[Enemy] = []
        self.npcs: List[NPC] = []
        self.resource_nodes: Dict[Tuple[int, int], str] = {}
        self._build_world()

    def _build_world(self) -> None:
        self.enemies.clear()
        self.npcs.clear()
        self.resource_nodes.clear()
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                world_pos = (x * self.tile_size, y * self.tile_size)
                if tile == "P":
                    self.spawn_point = world_pos
                elif tile == "E":
                    enemy_id = random.choice(["slime", "goblin", "wolf"])
                    enemy = create_enemy(enemy_id, world_pos, self.tile_size)
                    if enemy:
                        self.enemies.append(enemy)
                elif tile == "N":
                    self.npcs.append(self._create_npc(world_pos))
                elif tile == "T":
                    self.resource_nodes[(x, y)] = "herb"

    def _create_npc(self, position: Tuple[int, int]) -> NPC:
        quest_dialogue = DialogueTree(
            [
                DialogueNode(
                    text="Greetings, traveler! Monsters have been troubling our forest.",
                    options=[
                        DialogueOption("I will help.", next_node=1, action="accept_quest"),
                        DialogueOption("I cannot right now.", next_node=2),
                    ],
                ),
                DialogueNode(
                    text="Thank you! Defeat three forest slimes to keep us safe.",
                    options=[DialogueOption("I will return soon.", next_node=None)],
                ),
                DialogueNode(
                    text="Stay safe on the road.",
                    options=[DialogueOption("Farewell.", next_node=None)],
                ),
            ]
        )
        return NPC(name="Elder Rowan", position=position, tile_size=self.tile_size, dialogue_tree=quest_dialogue, quest_id="slime_cull")

    def is_walkable(self, tile_x: int, tile_y: int) -> bool:
        if tile_x < 0 or tile_y < 0 or tile_x >= self.width or tile_y >= self.height:
            return False
        tile = self.map_data[tile_y][tile_x]
        return tile in {".", "P", "E", "N", "T"}

    def is_walkable_rect(self, rect: pygame.Rect) -> bool:
        corners = {
            (rect.left // self.tile_size, rect.top // self.tile_size),
            ((rect.right - 1) // self.tile_size, rect.top // self.tile_size),
            (rect.left // self.tile_size, (rect.bottom - 1) // self.tile_size),
            ((rect.right - 1) // self.tile_size, (rect.bottom - 1) // self.tile_size),
        }
        return all(self.is_walkable(x, y) for x, y in corners)

    def draw(self, surface) -> None:  # noqa: ANN001 - pygame surface
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                colour = TILE_COLOURS.get(tile, TILE_COLOURS.get(".", (60, 110, 60)))
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                pygame.draw.rect(surface, colour, rect)

        for position in self.resource_nodes:
            x, y = position
            rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
            pygame.draw.rect(surface, (20, 180, 90), rect)

        for npc in self.npcs:
            npc.draw(surface)

        for enemy in self.enemies:
            enemy.draw(surface)

    def enemy_at_player(self, player_rect: pygame.Rect) -> Optional[Enemy]:
        for enemy in self.enemies:
            if enemy.rect.colliderect(player_rect):
                return enemy
        return None

    def npc_near_player(self, player_rect: pygame.Rect) -> Optional[NPC]:
        for npc in self.npcs:
            if npc.rect.colliderect(player_rect):
                return npc
        return None

    def harvest_resource(self, player_rect: pygame.Rect):
        tile_coords = (player_rect.centerx // self.tile_size, player_rect.centery // self.tile_size)
        if tile_coords in self.resource_nodes:
            item_id = self.resource_nodes.pop(tile_coords)
            return create_item(item_id)
        return None

    def remove_enemy(self, enemy: Enemy) -> None:
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def to_dict(self) -> Dict:
        return {
            "enemies": [
                {
                    "id": enemy.enemy_id,
                    "position": [enemy.rect.x, enemy.rect.y],
                    "health": enemy.stats["health"],
                }
                for enemy in self.enemies
            ],
            "resources": [
                {"position": [x, y], "item": item_id} for (x, y), item_id in self.resource_nodes.items()
            ],
        }

    def load_state(self, payload: Dict) -> None:
        self._build_world()
        self.enemies.clear()
        for entry in payload.get("enemies", []):
            enemy = create_enemy(entry["id"], tuple(entry["position"]), self.tile_size)
            if enemy:
                enemy.stats["health"] = entry.get("health", enemy.stats["health"])
                self.enemies.append(enemy)
        self.resource_nodes.clear()
        for entry in payload.get("resources", []):
            position = tuple(entry["position"])
            self.resource_nodes[position] = entry["item"]

    def get_default_quest(self) -> Quest:
        return Quest(
            quest_id="slime_cull",
            name="Forest Cleaning",
            description="Defeat three forest slimes to keep the path clear.",
            goal_type="slay",
            target="slime",
            required=3,
            reward_experience=120,
            reward_items=["health_potion"],
        )