class Skill:
    def __init__(self, name, damage_multiplier, mana_cost, cooldown):
        self.name = name
        self.damage_multiplier = damage_multiplier
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.current_cooldown = 0

class CombatSystem:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.skills = [
            Skill("Fireball", 1.5, 20, 3),
            Skill("Shield Bash", 1.2, 10, 2)
        ]

    def use_skill(self, skill_index):
        skill = self.skills[skill_index]
        if self.player.stats['mana'] >= skill.mana_cost and skill.current_cooldown == 0:
            damage = self.player.stats['attack'] * skill.damage_multiplier
            self.enemy.health -= damage
            self.player.stats['mana'] -= skill.mana_cost
            skill.current_cooldown = skill.cooldown
            return f"Used {skill.name} for {damage} damage!"
        return "Can't use that skill now!"

    def update_cooldowns(self):
        for skill in self.skills:
            if skill.current_cooldown > 0:
                skill.current_cooldown -= 1