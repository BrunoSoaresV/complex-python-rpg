import pygame

class Player:
    def __init__(self):
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.speed = 5
        
        # Character stats
        self.level = 1
        self.exp = 0
        self.stats = {
            'health': 100,
            'attack': 10,
            'defense': 5,
            'magic': 3
        }
        
    def move(self, direction):
        if direction == 'up':
            self.rect.y -= self.speed
        elif direction == 'down':
            self.rect.y += self.speed
        elif direction == 'left':
            self.rect.x -= self.speed
        elif direction == 'right':
            self.rect.x += self.speed
            
    def update(self):
        # Keep player within screen bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, 1280, 720))
            
    def draw(self, surface):
        surface.blit(self.image, self.rect)