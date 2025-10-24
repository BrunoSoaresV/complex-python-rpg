from dialogue import DialogueTree, DialogueNode

class NPC:
    def __init__(self, name, dialogue_tree):
        self.name = name
        self.dialogue_tree = dialogue_tree

    def start_dialogue(self):
        return self.dialogue_tree