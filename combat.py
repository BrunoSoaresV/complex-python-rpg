from skills import Skill

class CombatSystem:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.turn_count = 0

    def skill_turn(self):
        # Display available skills and handle selection
        self.turn_count += 1
        for skill in self.player.skills:
            skill.cooldown = max(0, skill.cooldown - 1)