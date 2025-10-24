class DialogueNode:
    def __init__(self, text, options):
        self.text = text
        self.options = options  # List of (choice_text, next_node_index)

class DialogueTree:
    def __init__(self):
        self.nodes = []
        self.current_node = 0

    def add_node(self, text, options):
        self.nodes.append(DialogueNode(text, options))

    def interact(self):
        while self.current_node is not None:
            current = self.nodes[self.current_node]
            print(f"\n{current.text}")
            for i, (text, _) in enumerate(current.options):
                print(f"{i+1}. {text}")
            choice = int(input("Choose an option: ")) - 1
            _, self.current_node = current.options[choice]