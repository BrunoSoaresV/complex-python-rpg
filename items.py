"""Lightweight item system used across gameplay subsystems."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional


@dataclass(slots=True)
class Item:
    name: str
    item_type: str
    description: str = ""

    def can_use(self) -> bool:
        return False

    def apply(self, player, target=None) -> str:  # noqa: ANN001 - dynamic target
        raise NotImplementedError("Base items are not directly usable.")


@dataclass(slots=True)
class Consumable(Item):
    heal_amount: int = 0
    mana_amount: int = 0

    def can_use(self) -> bool:
        return True

    def apply(self, player, target=None) -> str:  # noqa: ANN001 - dynamic target
        healed = 0
        restored = 0
        if self.heal_amount:
            healed = player.heal(self.heal_amount)
        if self.mana_amount:
            restored = player.restore_mana(self.mana_amount)
        segments = []
        if healed:
            segments.append(f"restored {healed} HP")
        if restored:
            segments.append(f"recovered {restored} MP")
        return f"Used {self.name} and " + " and ".join(segments) if segments else f"Used {self.name}."


@dataclass(slots=True)
class Equipment(Item):
    stats: Dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class Resource(Item):
    rarity: str = "common"


def _health_potion() -> Consumable:
    return Consumable(
        name="Health Potion",
        item_type="consumable",
        description="Restores a small amount of health.",
        heal_amount=35,
    )


def _mana_potion() -> Consumable:
    return Consumable(
        name="Mana Potion",
        item_type="consumable",
        description="Restores a small amount of mana.",
        mana_amount=25,
    )


def _herb() -> Resource:
    return Resource(
        name="Herb",
        item_type="resource",
        description="A fresh herb used in alchemy recipes.",
        rarity="common",
    )


def _ore() -> Resource:
    return Resource(
        name="Iron Ore",
        item_type="resource",
        description="Chunk of raw iron ready to be smelted.",
        rarity="uncommon",
    )


ITEM_LIBRARY: Dict[str, Callable[[], Item]] = {
    "health_potion": _health_potion,
    "mana_potion": _mana_potion,
    "herb": _herb,
    "iron_ore": _ore,
}


def create_item(item_id: str) -> Optional[Item]:
    factory = ITEM_LIBRARY.get(item_id)
    return factory() if factory else None


def serialise_item(item: Item) -> Dict[str, str]:
    return {"id": resolve_item_id(item), "name": item.name}


def resolve_item_id(item: Item) -> str:
    for key, factory in ITEM_LIBRARY.items():
        if factory().name == item.name:
            return key
    return item.name.lower().replace(" ", "_")


def deserialise_item(payload: Dict[str, str]) -> Optional[Item]:
    return create_item(payload.get("id", ""))