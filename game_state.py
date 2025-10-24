from __future__ import annotations

from collections import deque
from typing import Deque, Optional

import pygame

from combat import CombatSystem
from crafting import CraftingSystem
from items import create_item
from player import Player
from quests import Quest, QuestSystem
from save_system import SaveSystem
from world import World


class GameState:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.mode = "explore"
        self.world = World()
        self.player = Player(self.world.spawn_point, self.world.tile_size)
        self.crafting = CraftingSystem()
        self.quests = QuestSystem()
        self.save_system = SaveSystem()
        self.message_log: Deque[str] = deque(maxlen=6)
        self.font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 24)

        self.combat: Optional[CombatSystem] = None
        self.dialogue_npc = None
        self.dialogue_selection = 0
        self.inventory_selection = 0
        self.crafting_selection = 0

        self.load_saved_game()
        self.message_log.append("Welcome to the frontier.")

    # ------------------------------------------------------------------
    # High-level control
    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if self.mode == "explore":
            self._handle_explore_input(event.key)
        elif self.mode == "combat":
            self._handle_combat_input(event.key)
        elif self.mode == "dialogue":
            self._handle_dialogue_input(event.key)
        elif self.mode == "inventory":
            self._handle_inventory_input(event.key)
        elif self.mode == "crafting":
            self._handle_crafting_input(event.key)

    def update(self, delta_time: float) -> None:
        if self.mode == "explore":
            self.player.update(delta_time)
            encounter = self.world.enemy_at_player(self.player.rect)
            if encounter and not self.combat:
                self.start_combat(encounter)

        if self.mode == "combat" and self.combat:
            if self.combat.outcome == "victory":
                self.finish_combat(victory=True)
            elif self.combat.outcome == "defeat":
                self.finish_combat(victory=False)

    def draw(self) -> None:
        self.world.draw(self.screen)
        self.player.draw(self.screen)
        self._draw_ui()

        if self.mode == "combat" and self.combat:
            self._draw_combat_overlay()
        elif self.mode == "dialogue":
            self._draw_dialogue_overlay()
        elif self.mode == "inventory":
            self._draw_inventory_overlay()
        elif self.mode == "crafting":
            self._draw_crafting_overlay()

    # ------------------------------------------------------------------
    # Input handling per mode
    # ------------------------------------------------------------------
    def _handle_explore_input(self, key: int) -> None:
        if key == pygame.K_UP:
            self.player.move("up", self.world)
        elif key == pygame.K_DOWN:
            self.player.move("down", self.world)
        elif key == pygame.K_LEFT:
            self.player.move("left", self.world)
        elif key == pygame.K_RIGHT:
            self.player.move("right", self.world)
        elif key == pygame.K_e:
            self._interact()
        elif key == pygame.K_i:
            self.mode = "inventory"
            self.inventory_selection = 0
        elif key == pygame.K_c:
            self.mode = "crafting"
            self.crafting_selection = 0
        elif key == pygame.K_s:
            self.save_current_game()
        elif key == pygame.K_l:
            self.load_saved_game()

    def _handle_combat_input(self, key: int) -> None:
        if not self.combat:
            return
        if key == pygame.K_1:
            self.combat.player_basic_attack()
        elif key == pygame.K_2:
            self.combat.player_use_skill(0)
        elif key == pygame.K_3:
            self.combat.player_use_skill(1)
        elif key == pygame.K_6:
            self.combat.player_use_skill(2)
        elif key == pygame.K_4:
            self.combat.player_use_consumable("health_potion")
        elif key == pygame.K_5:
            self.combat.player_use_consumable("mana_potion")
        elif key == pygame.K_ESCAPE:
            self.message_log.append("You flee from battle.")
            self.mode = "explore"
            self.combat = None
            self.player.rect.topleft = self.world.spawn_point

    def _handle_dialogue_input(self, key: int) -> None:
        npc = self.dialogue_npc
        if not npc:
            return
        options = npc.dialogue_tree.current().options
        if key in (pygame.K_UP, pygame.K_w):
            self.dialogue_selection = (self.dialogue_selection - 1) % len(options)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.dialogue_selection = (self.dialogue_selection + 1) % len(options)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            action, has_next = npc.dialogue_tree.choose(self.dialogue_selection)
            if action == "accept_quest" and npc.quest_id:
                self._accept_quest(npc.quest_id)
                npc.has_given_quest = True
            if not has_next:
                self.mode = "explore"
                self.dialogue_npc = None
                self.dialogue_selection = 0

    def _handle_inventory_input(self, key: int) -> None:
        items = self.player.inventory
        if not items:
            if key in (pygame.K_ESCAPE, pygame.K_i):
                self.mode = "explore"
            return
        if key in (pygame.K_UP, pygame.K_w):
            self.inventory_selection = (self.inventory_selection - 1) % len(items)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.inventory_selection = (self.inventory_selection + 1) % len(items)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            item_id = self.player.list_inventory_ids()[self.inventory_selection]
            message = self.player.consume_item(item_id)
            self.message_log.append(message)
            if "No " not in message:
                self.mode = "explore"
        elif key in (pygame.K_ESCAPE, pygame.K_i):
            self.mode = "explore"

    def _handle_crafting_input(self, key: int) -> None:
        recipes = list(self.crafting.recipes.keys())
        if key in (pygame.K_ESCAPE, pygame.K_c):
            self.mode = "explore"
            return
        if not recipes:
            return
        if key in (pygame.K_UP, pygame.K_w):
            self.crafting_selection = (self.crafting_selection - 1) % len(recipes)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.crafting_selection = (self.crafting_selection + 1) % len(recipes)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            recipe = recipes[self.crafting_selection]
            result = self.crafting.craft(self.player, recipe)
            self.message_log.append(result)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _interact(self) -> None:
        npc = self.world.npc_near_player(self.player.rect)
        if npc:
            self.mode = "dialogue"
            self.dialogue_npc = npc
            npc.start_dialogue()
            self.dialogue_selection = 0
            return
        resource = self.world.harvest_resource(self.player.rect)
        if resource:
            self.player.add_item(resource)
            self.message_log.append(f"Gathered {resource.name}.")

    def start_combat(self, enemy) -> None:  # noqa: ANN001 - enemy runtime type
        self.combat = CombatSystem(self.player, enemy)
        self.mode = "combat"

    def finish_combat(self, victory: bool) -> None:
        if not self.combat:
            return
        enemy = self.combat.enemy
        if victory:
            self.message_log.append(f"Defeated {enemy.name}!")
            self.player.gain_experience(enemy.experience)
            loot = enemy.drop_loot()
            for item in loot:
                self.player.add_item(item)
                self.message_log.append(f"Found {item.name}.")
            completions = self.quests.record_event("slay", enemy.enemy_id)
            if completions:
                finished = self.quests.remove_completed()
                for quest in finished:
                    self._reward_quest(quest)
            self.world.remove_enemy(enemy)
        else:
            self.message_log.append("You were defeated. Returning to camp...")
            self.player.stats["health"] = self.player.stats["max_health"]
            self.player.stats["mana"] = self.player.stats["max_mana"]
            self.player.rect.topleft = self.world.spawn_point
            enemy.stats["health"] = enemy.max_health
        self.mode = "explore"
        self.combat = None

    def _reward_quest(self, quest: Quest) -> None:
        self.player.gain_experience(quest.reward_experience)
        for item_id in quest.reward_items:
            item = create_item(item_id)
            if item:
                self.player.add_item(item)
        self.message_log.append(f"Quest complete: {quest.name}!")

    def _accept_quest(self, quest_id: str) -> None:
        if quest_id == "slime_cull":
            quest = self.world.get_default_quest()
            message = self.quests.add_quest(quest)
            self.message_log.append(message)

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _draw_ui(self) -> None:
        stats = self.player.stats
        stat_text = f"HP {stats['health']}/{stats['max_health']}  MP {stats['mana']}/{stats['max_mana']}  LV {stats['level']}"
        surface = self.font.render(stat_text, True, (255, 255, 255))
        self.screen.blit(surface, (8, 8))

        y = self.screen.get_height() - 20 * len(self.message_log) - 10
        for message in self.message_log:
            text_surface = self.font.render(message, True, (240, 240, 240))
            self.screen.blit(text_surface, (10, y))
            y += 20

        quest_y = 40
        if self.quests.active:
            header = self.font.render("Quests:", True, (255, 255, 200))
            self.screen.blit(header, (8, quest_y))
            quest_y += 20
            for quest in self.quests.list_active():
                text = f"{quest.name}: {quest.progress}/{quest.required}"
                entry_surface = self.font.render(text, True, (220, 220, 180))
                self.screen.blit(entry_surface, (10, quest_y))
                quest_y += 20

    def _draw_combat_overlay(self) -> None:
        width, height = self.screen.get_size()
        panel = pygame.Surface((width, 180))
        panel.set_alpha(200)
        panel.fill((20, 20, 20))
        self.screen.blit(panel, (0, height - 180))

        enemy = self.combat.enemy
        lines = [
            f"Facing {enemy.name}",
            f"Enemy HP: {enemy.stats['health']}/{enemy.max_health}",
            "Actions: 1-Attack 2-Fireball 3-Heal 4-Use HP Potion 5-Use MP Potion",
        ]
        for index, line in enumerate(lines):
            text = self.big_font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (20, height - 170 + index * 30))

        y = height - 80
        for entry in self.combat.round_log:
            text = self.font.render(entry, True, (200, 200, 200))
            self.screen.blit(text, (20, y))
            y += 20

    def _draw_dialogue_overlay(self) -> None:
        npc = self.dialogue_npc
        if not npc:
            return
        width, height = self.screen.get_size()
        panel = pygame.Surface((width - 40, 200))
        panel.set_alpha(220)
        panel.fill((30, 30, 50))
        self.screen.blit(panel, (20, height - 220))

        node = npc.dialogue_tree.current()
        text_surface = self.big_font.render(node.text, True, (255, 255, 255))
        self.screen.blit(text_surface, (40, height - 210))

        for index, option in enumerate(node.options):
            colour = (255, 255, 0) if index == self.dialogue_selection else (220, 220, 220)
            option_surface = self.font.render(option.text, True, colour)
            self.screen.blit(option_surface, (60, height - 150 + index * 24))

    def _draw_inventory_overlay(self) -> None:
        width, height = self.screen.get_size()
        panel = pygame.Surface((width - 160, height - 160))
        panel.set_alpha(220)
        panel.fill((40, 40, 40))
        self.screen.blit(panel, (80, 80))

        title = self.big_font.render("Inventory", True, (255, 255, 255))
        self.screen.blit(title, (120, 100))

        if not self.player.inventory:
            empty = self.font.render("Inventory empty.", True, (200, 200, 200))
            self.screen.blit(empty, (120, 140))
            return

        for index, item in enumerate(self.player.inventory):
            colour = (255, 240, 120) if index == self.inventory_selection else (220, 220, 220)
            text = f"{item.name} - {item.description}"
            entry = self.font.render(text, True, colour)
            self.screen.blit(entry, (120, 140 + index * 24))

    def _draw_crafting_overlay(self) -> None:
        width, height = self.screen.get_size()
        panel = pygame.Surface((width - 160, height - 160))
        panel.set_alpha(220)
        panel.fill((50, 45, 35))
        self.screen.blit(panel, (80, 80))

        title = self.big_font.render("Crafting", True, (255, 255, 255))
        self.screen.blit(title, (120, 100))

        recipes = list(self.crafting.recipes.items())
        if not recipes:
            empty = self.font.render("No recipes available.", True, (200, 200, 200))
            self.screen.blit(empty, (120, 140))
            return

        for index, (item_name, components) in enumerate(recipes):
            colour = (255, 240, 120) if index == self.crafting_selection else (220, 220, 220)
            component_summary = ", ".join(f"{key}x{value}" for key, value in components.items())
            text = f"{item_name.replace('_', ' ')} <- {component_summary}"
            entry = self.font.render(text, True, colour)
            self.screen.blit(entry, (120, 140 + index * 24))

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def save_current_game(self) -> None:
        self.save_system.save_game(self.player, self.world, self.quests)
        self.message_log.append("Game saved.")

    def load_saved_game(self) -> None:
        payload = self.save_system.load_game()
        if not payload:
            self.player = Player(self.world.spawn_point, self.world.tile_size)
            return
        self.player = Player.from_dict(payload.get("player", {}), self.world.tile_size)
        self.world.load_state(payload.get("world", {}))
        self.quests.from_dict(payload.get("quests", {}))
        self.message_log.append("Loaded saved game.")
