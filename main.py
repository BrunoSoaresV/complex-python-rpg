"""Entry point for the RPG."""

import pygame

from game_state import GameState


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Python RPG")
    clock = pygame.time.Clock()

    game_state = GameState(screen)

    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game_state.handle_event(event)

        game_state.update(delta_time)
        screen.fill((0, 0, 0))
        game_state.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()