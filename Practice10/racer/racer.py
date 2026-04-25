import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 400, 600
ROAD_X, ROAD_W = 50, 300
FPS = 60

WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
GRAY       = (60, 60, 60)
GREEN      = (34, 139, 34)
YELLOW     = (255, 220, 0)
BLUE       = (50, 100, 220)
RED        = (220, 50, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22, bold=True)


def draw_car(surface, rect, color):
    pygame.draw.rect(surface, color, rect, border_radius=6)
    win = pygame.Rect(rect.x + 8, rect.y + 10, rect.width - 16, 20)
    pygame.draw.rect(surface, (180, 220, 255), win, border_radius=4)
    for wx, wy in [(rect.x - 7, rect.y + 8), (rect.right - 3, rect.y + 8),
                   (rect.x - 7, rect.bottom - 26), (rect.right - 3, rect.bottom - 26)]:
        pygame.draw.rect(surface, BLACK, (wx, wy, 10, 18), border_radius=3)


def main():
    line_y = [i * 80 for i in range(9)]

    player = pygame.Rect(WIDTH // 2 - 20, HEIGHT - 110, 40, 70)

    enemies = []
    coins   = []

    enemy_timer = 0
    coin_timer  = random.randint(80, 150)

    score      = 0
    coin_count = 0
    speed      = 5
    game_over  = False
    running    = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                main()
                return

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > ROAD_X + 5:
                player.x -= 5
            if keys[pygame.K_RIGHT] and player.right < ROAD_X + ROAD_W - 5:
                player.x += 5

            speed = 5 + score // 5

            for i in range(len(line_y)):
                line_y[i] += speed
                if line_y[i] > HEIGHT:
                    line_y[i] -= 9 * 80

            enemy_timer += 1
            if enemy_timer >= max(40, 90 - score * 2):
                x = random.randint(ROAD_X + 5, ROAD_X + ROAD_W - 45)
                color = random.choice([(200, 50, 50), (50, 180, 50), (200, 130, 50)])
                enemies.append([pygame.Rect(x, -75, 40, 70), color])
                enemy_timer = 0

            coin_timer -= 1
            if coin_timer <= 0:
                x = random.randint(ROAD_X + 15, ROAD_X + ROAD_W - 25)
                coins.append(pygame.Rect(x, -20, 20, 20))
                coin_timer = random.randint(60, 120)

            for e in enemies[:]:
                e[0].y += speed
                if e[0].colliderect(player):
                    game_over = True
                if e[0].top > HEIGHT:
                    enemies.remove(e)
                    score += 1

            for c in coins[:]:
                c.y += speed
                if c.colliderect(player):
                    coin_count += 1
                    coins.remove(c)
                elif c.top > HEIGHT:
                    coins.remove(c)

        screen.fill(GREEN)
        pygame.draw.rect(screen, GRAY, (ROAD_X, 0, ROAD_W, HEIGHT))

        for y in line_y:
            pygame.draw.rect(screen, YELLOW, (WIDTH // 2 - 4, y, 8, 45))

        for c in coins:
            pygame.draw.circle(screen, YELLOW, c.center, 10)
            pygame.draw.circle(screen, (200, 160, 0), c.center, 10, 2)

        for e in enemies:
            draw_car(screen, e[0], e[1])
        draw_car(screen, player, BLUE)

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))

        coin_text = font.render(f"Coins: {coin_count}", True, YELLOW)
        screen.blit(coin_text, (WIDTH - coin_text.get_width() - 10, 10))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            go = font.render("GAME OVER", True, RED)
            rr = font.render("Press R to restart", True, WHITE)
            screen.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT // 2 - 30))
            screen.blit(rr, (WIDTH // 2 - rr.get_width() // 2, HEIGHT // 2 + 15))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
