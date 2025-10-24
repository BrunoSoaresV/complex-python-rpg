from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Skill:
    name: str
    cost: int
    cooldown_turns: int
    description: str
    current_cooldown: int = 0

    def can_use(self, caster) -> bool:  # noqa: ANN001 - dynamic entity
        return caster.stats["mana"] >= self.cost and self.current_cooldown == 0

    def trigger_cooldown(self) -> None:
        self.current_cooldown = self.cooldown_turns

    def tick(self) -> None:
        if self.current_cooldown:
            self.current_cooldown -= 1

    def execute(self, caster, target) -> str:  # noqa: ANN001 - dynamic target
        raise NotImplementedError


class Fireball(Skill):
    def __init__(self):
        super().__init__(
            name="Fireball",
            cost=15,
            cooldown_turns=2,
            description="Deal heavy fire damage to a single target.",
        )

    def execute(self, caster, target) -> str:  # noqa: ANN001
        damage = max((caster.stats["magic"] * 2) - target.stats.get("resistance", 0), 4)
        target.take_damage(damage)
        caster.stats["mana"] -= self.cost
        self.trigger_cooldown()
        return f"Cast Fireball for {damage} damage!"


class HealingLight(Skill):
    def __init__(self):
        super().__init__(
            name="Healing Light",
            cost=12,
            cooldown_turns=3,
            description="Restore a moderate amount of health.",
        )

    def execute(self, caster, target=None) -> str:  # noqa: ANN001
        amount = max(caster.stats["magic"] + 12, 10)
        restored = caster.heal(amount)
        caster.stats["mana"] -= self.cost
        self.trigger_cooldown()
        return f"Healing Light restored {restored} HP."


class ArcaneShield(Skill):
    def __init__(self):
        super().__init__(
            name="Arcane Shield",
            cost=10,
            cooldown_turns=4,
            description="Raise defense temporarily.",
        )

    def execute(self, caster, target=None) -> str:  # noqa: ANN001
        caster.add_temporary_buff("defense", 5, duration=3)
        caster.stats["mana"] -= self.cost
        self.trigger_cooldown()
        return "Arcane Shield raises defense!"