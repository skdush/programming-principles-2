import pygame
import sys
from ball import Ball

WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
BLUE = (50, 100, 200)


def draw_grid(screen, width, height, step=40):
    for x in range(0, width, step):
        pygame.draw.line(screen, LIGHT_GRAY, (x, 0), (x, height))
    for y in range(0, height, step):
        pygame.draw.line(screen, LIGHT_GRAY, (0, y), (width, y))


def draw_hud(screen, ball, font_med, font_small):
    pygame.draw.rect(screen, (240, 240, 250), (0, HEIGHT - 60, WIDTH, 60))
    pygame.draw.line(screen, DARK_GRAY, (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 2)

    coord_text = f"Position: X={ball.x}  Y={ball.y}"
    coord_surf = font_med.render(coord_text, True, BLUE)
    screen.blit(coord_surf, (20, HEIGHT - 45))

    hint = font_small.render(
        "Arrow Keys — move  |  ESC — quit", True, DARK_GRAY
    )
    screen.blit(hint, (WIDTH - hint.get_width() - 20, HEIGHT - 42))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball Game")
    clock = pygame.time.Clock()

    ball = Ball(WIDTH, HEIGHT - 60)

    font_title = pygame.font.SysFont("Arial", 22, bold=True)
    font_med = pygame.font.SysFont("Arial", 20)
    font_small = pygame.font.SysFont("Arial", 16)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            ball.move("up")
        if keys[pygame.K_DOWN]:
            ball.move("down")
        if keys[pygame.K_LEFT]:
            ball.move("left")
        if keys[pygame.K_RIGHT]:
            ball.move("right")

        screen.fill(WHITE)
        draw_grid(screen, WIDTH, HEIGHT - 60)

        pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, HEIGHT - 60), 3)

        title = font_title.render("Moving Ball Game — use Arrow Keys", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 8))

        ball.draw(screen)

        draw_hud(screen, ball, font_med, font_small)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
