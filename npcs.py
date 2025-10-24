from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import pygame

from dialogue import DialogueTree


@dataclass
class NPC:
    name: str
    position: Tuple[int, int]
    tile_size: int
    dialogue_tree: DialogueTree
    quest_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.rect = pygame.Rect(self.position[0], self.position[1], self.tile_size, self.tile_size)
        self.color = (230, 220, 120)
        self.has_given_quest = False

    def draw(self, surface) -> None:  # noqa: ANN001 - pygame surface
        pygame.draw.rect(surface, self.color, self.rect)

    def start_dialogue(self) -> DialogueTree:
        self.dialogue_tree.reset()
        return self.dialogue_tree