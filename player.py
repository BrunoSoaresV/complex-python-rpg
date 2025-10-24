class Player:
    def __init__(self):
        self.skills = []
        self.mana = 100

    def learn_skill(self, skill):
        self.skills.append(skill)