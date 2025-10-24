class DialogueNode:
    def __init__(self, text, options):
        self.text = text
        self.options = options  # List of (option_text, next_node)

class DialogueTree:
    def __init__(self, root_node):
        self.current_node = root_node

    def get_current_dialogue(self):
        return self.current_node

    def select_option(self, index):
        if 0 <= index < len(self.current_node.options):
            self.current_node = self.current_node.options[index][1]
            return True
        return False