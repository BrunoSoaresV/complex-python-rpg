from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(slots=True)
class DialogueOption:
    text: str
    next_node: Optional[int] = None
    action: Optional[str] = None


@dataclass(slots=True)
class DialogueNode:
    text: str
    options: List[DialogueOption]


class DialogueTree:
    def __init__(self, nodes: List[DialogueNode]) -> None:
        self.nodes = nodes
        self.current_index = 0

    def current(self) -> DialogueNode:
        return self.nodes[self.current_index]

    def choose(self, option_index: int) -> Tuple[Optional[str], bool]:
        node = self.current()
        if option_index < 0 or option_index >= len(node.options):
            return None, True
        option = node.options[option_index]
        has_next = option.next_node is not None
        if has_next:
            self.current_index = option.next_node
        return option.action, has_next

    def reset(self) -> None:
        self.current_index = 0