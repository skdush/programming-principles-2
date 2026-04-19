import pygame
import sys
from clock import MickeysClock

# Настройки окна
WIDTH, HEIGHT = 600, 650
FPS = 60
BG_COLOR = (240, 240, 255)

TITLE_COLOR = (30, 30, 100)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mickey's Clock")
    clock_tick = pygame.time.Clock()

    # Создаём объект часов
    clock = MickeysClock(screen, WIDTH, HEIGHT - 60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Фон
        screen.fill(BG_COLOR)

        # Заголовок
        font = pygame.font.SysFont("Arial", 26, bold=True)
        title = font.render("Mickey's Clock - Minutes & Seconds", True, TITLE_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

        # Рисуем часы
        clock.draw()

        pygame.display.flip()
        clock_tick.tick(FPS)


if __name__ == "__main__":
    main()
