# NPC interaction system
class NPC:
    def __init__(self, name, dialogue, quests):
        self.name = name
        self.dialogue = dialogue
        self.quests = quests

    def interact(self, player):
        print(f"{self.name}: {self.dialogue}")
        if self.quests:
            player.quest_system.add_quest(self.quests[0])