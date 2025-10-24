import pygame
from items import Item

class Player:
    def __init__(self):
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.speed = 5
        
        # Enhanced progression system
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        self.skill_points = 0
        
        # Stats system with equipment bonuses
 ... (rest of the enhanced player class) ...