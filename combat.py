from __future__ import annotations

from collections import deque
from typing import Deque, Optional


class CombatSystem:
    """Simple turn-based combat controller."""

    def __init__(self, player, enemy):  # noqa: ANN001 - runtime entities
        self.player = player
        self.enemy = enemy
        self.turn = "player"
        self.round_log: Deque[str] = deque(maxlen=8)
        self.outcome: Optional[str] = None

        # Reset skill cooldowns when entering combat
        for skill in self.player.skills:
            skill.current_cooldown = 0

        self.round_log.append(f"A wild {enemy.name} appears!")

    def player_basic_attack(self) -> None:
        if not self._can_take_action():
            return
        damage = max(self.player.stats["attack"] - self.enemy.stats.get("defense", 0), 2)
        self.enemy.take_damage(damage)
        self.round_log.append(f"You strike for {damage} damage.")
        self._after_player_action()

    def player_use_skill(self, index: int) -> None:
        if not self._can_take_action():
            return
        if index < 0 or index >= len(self.player.skills):
            self.round_log.append("Invalid skill selection.")
            return
        skill = self.player.skills[index]
        if not skill.can_use(self.player):
            self.round_log.append(f"Cannot use {skill.name} right now.")
            return
        result = skill.execute(self.player, self.enemy)
        self.round_log.append(result)
        self._after_player_action()

    def player_use_consumable(self, item_id: str) -> None:
        if not self._can_take_action():
            return
        message = self.player.consume_item(item_id)
        self.round_log.append(message)
        self._after_player_action(skip_enemy=message.startswith("No "))

    def enemy_turn(self) -> None:
        if not self.enemy.is_alive():
            return
        damage = max(self.enemy.stats["attack"] - self.player.stats.get("defense", 0), 1)
        self.player.take_damage(damage)
        self.round_log.append(f"{self.enemy.name} hits you for {damage} damage.")
        if not self.player.is_alive():
            self.outcome = "defeat"
        else:
            self.turn = "player"
            self.player.tick_buffs()
            for skill in self.player.skills:
                skill.tick()

    def _after_player_action(self, skip_enemy: bool = False) -> None:
        if not self.enemy.is_alive():
            self.outcome = "victory"
            self.round_log.append(f"{self.enemy.name} is defeated!")
            return
        self.turn = "enemy"
        if skip_enemy:
            self.turn = "player"
            return
        self.enemy_turn()

    def _can_take_action(self) -> bool:
        return self.turn == "player" and self.outcome is None