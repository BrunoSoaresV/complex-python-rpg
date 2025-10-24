# Main game loop and initialization
import pygame
from game_state import GameState
from player import Player
from world import World

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('Python RPG')
    
    game_state = GameState()
    player = Player()
    world = World()
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle player input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move('up')
                elif event.key == pygame.K_DOWN:
                    player.move('down')
                elif event.key == pygame.K_LEFT:
                    player.move('left')
                elif event.key == pygame.K_RIGHT:
                    player.move('right')
        
        # Update game state
        world.update()
        player.update()
        
        # Render
        screen.fill((0, 0, 0))
        world.draw(screen)
        player.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()