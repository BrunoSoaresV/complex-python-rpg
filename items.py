# Item classes and inventory management
class Item:
    def __init__(self, name, item_type, stats):
        self.name = name
        self.type = item_type
        self.stats = stats

class Weapon(Item):
    def __init__(self, name, damage):
        super().__init__(name, 'weapon', {'attack': damage})

class Armor(Item):
    def __init__(self, name, defense):
        super().__init__(name, 'armor', {'defense': defense})