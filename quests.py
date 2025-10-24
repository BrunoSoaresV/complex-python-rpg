from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Quest:
   quest_id: str
   name: str
   description: str
   goal_type: str
   target: str
   required: int
   reward_experience: int
   completed: bool = False
   progress: int = 0
   reward_items: List[str] = field(default_factory=list)

   def record_progress(self, goal_type: str, target: str) -> bool:
      if self.completed or goal_type != self.goal_type or target != self.target:
         return False
      self.progress = min(self.progress + 1, self.required)
      if self.progress >= self.required:
         self.completed = True
      return self.completed


class QuestSystem:
   def __init__(self) -> None:
      self.active: Dict[str, Quest] = {}

   def add_quest(self, quest: Quest) -> str:
      if quest.quest_id in self.active:
         return "Quest already active."
      self.active[quest.quest_id] = quest
      return f"Quest accepted: {quest.name}."

   def record_event(self, goal_type: str, target: str) -> List[Quest]:
      completed: List[Quest] = []
      for quest in self.active.values():
         if quest.record_progress(goal_type, target) and quest not in completed:
            completed.append(quest)
      return completed

   def remove_completed(self) -> List[Quest]:
      finished = [quest for quest in self.active.values() if quest.completed]
      for quest in finished:
         self.active.pop(quest.quest_id, None)
      return finished

   def to_dict(self) -> Dict:
      return {
         "quests": [
            {
               "quest_id": quest.quest_id,
               "name": quest.name,
               "description": quest.description,
               "goal_type": quest.goal_type,
               "target": quest.target,
               "required": quest.required,
               "progress": quest.progress,
               "completed": quest.completed,
               "reward_experience": quest.reward_experience,
               "reward_items": quest.reward_items,
            }
            for quest in self.active.values()
         ]
      }

   def from_dict(self, payload: Dict) -> None:
      self.active.clear()
      for entry in payload.get("quests", []):
         quest = Quest(
            quest_id=entry["quest_id"],
            name=entry["name"],
            description=entry["description"],
            goal_type=entry["goal_type"],
            target=entry["target"],
            required=entry["required"],
            reward_experience=entry.get("reward_experience", 0),
            reward_items=entry.get("reward_items", []),
         )
         quest.progress = entry.get("progress", 0)
         quest.completed = entry.get("completed", False)
         self.active[quest.quest_id] = quest

   def list_active(self) -> List[Quest]:
      return list(self.active.values())