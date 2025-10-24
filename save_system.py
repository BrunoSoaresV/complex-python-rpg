import json

class SaveSystem:
    def save_game(self, player, world):
        data = {
            'player': {
                'position': (player.rect.x, player.rect.y),
                'stats': player.stats,
                'inventory': [item.name for item in player.inventory]
            },
            'world_seed': world.seed
        }
        with open('save.json', 'w') as f:
            json.dump(data, f)

    def load_game(self):
        try:
            with open('save.json') as f:
                return json.load(f)
        except FileNotFoundError:
            return None