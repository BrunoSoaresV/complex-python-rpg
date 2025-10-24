import random

class Enemy:
    def __init__(self, name, health, attack):
        self.name = name
        self.health = health
        self.attack = attack

    def ai_move(self, player):
        # Simple AI: 70% chance to attack, 30% chance to defend
        if random.random() < 0.7:
            damage = self.attack - player.stats['defense']
            player.stats['health'] -= max(damage, 1)
            return f'{self.name} attacks!'
        else:
            self.health += 2
            return f'{self.name} defends!'