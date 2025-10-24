class CraftingSystem:
    def __init__(self):
        self.recipes = {
            'wooden_sword': {'sticks': 2, 'wood': 3},
            'iron_armor': {'iron_ingot': 5},
            'health_potion': {'herb': 3, 'water': 1}
        }

    def craft(self, player, item_name):
        if item_name in self.recipes:
            if self.has_ingredients(player, item_name):
                self.remove_ingredients(player, item_name)
                return f'Successfully crafted {item_name}'
        return 'Crafting failed'

    def has_ingredients(self, player, item_name):
        ... # 15 lines of ingredient checking logic