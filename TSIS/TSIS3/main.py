import pygame
import sys
from persistence import load_settings, add_score
from racer import Game, FPS, WIDTH, HEIGHT
from ui import main_menu, game_over_screen, leaderboard_screen, settings_screen

pygame.init()
screen   = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer — TSIS3")
clock    = pygame.time.Clock()

settings = load_settings()
username = "Player"


def run():
    global settings, username

    while True:
        action, username = main_menu(screen, clock, username)

        if action == "leaderboard":
            leaderboard_screen(screen, clock)
            continue

        if action == "settings":
            settings_screen(screen, clock, settings)
            continue

        game = Game(settings)

        while not game.game_over:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            game.update()
            game.draw(screen)
            pygame.display.flip()

        dist  = game.distance // 10
        coins = game.coin_count
        score = game.score
        add_score(username, score, dist, coins)

        result = game_over_screen(screen, clock, score, dist, coins)
        if result == "retry":
            game = Game(settings)
            continue


if __name__ == "__main__":
    run()
