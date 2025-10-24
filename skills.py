class Skill:
    def __init__(self, name, cost, effect):
        self.name = name
        self.cost = cost
        self.cooldown = 0

    def execute(self, caster, target):
        if caster.mana >= self.cost and self.cooldown == 0:
            caster.mana -= self.cost
            self.apply_effect(caster, target)
            self.cooldown = 3

class Fireball(Skill):
    def apply_effect(self, caster, target):
        damage = caster.magic * 2 - target.resistance
        target.take_damage(damage)