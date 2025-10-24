import json
from pathlib import Path


class SaveSystem:
    def __init__(self, save_path: str = "save.json") -> None:
        self.path = Path(save_path)

    def save_game(self, player, world, quest_system) -> None:  # noqa: ANN001 - runtime types
        payload = {
            "player": player.to_dict(),
            "world": world.to_dict(),
            "quests": quest_system.to_dict(),
        }
        self.path.write_text(json.dumps(payload, indent=2))

    def load_game(self):
        if not self.path.exists():
            return None
        return json.loads(self.path.read_text())