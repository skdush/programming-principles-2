import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
GREEN = (50, 200, 50)
DARK_GRAY = (40, 40, 40)
ROAD_COLOR = (60, 60, 60)
LINE_COLOR = (200, 200, 50)

ROAD_LEFT = 80
ROAD_RIGHT = 320
PLAYER_SPEED = 5
COIN_SPEED_BASE = 4
ENEMY_SPEED_BASE = 3
N_COINS_FOR_SPEEDUP = 5  # Enemy speeds up every N coins

# Coin types: (weight, color, points)
COIN_TYPES = [
    {"weight": 50, "color": YELLOW, "points": 1},   # common gold
    {"weight": 30, "color": (192, 192, 192), "points": 2},  # silver
    {"weight": 20, "color": (100, 200, 255), "points": 5},  # rare blue
]


def pick_coin_type():
    """Pick a coin type based on weights."""
    total = sum(c["weight"] for c in COIN_TYPES)
    r = random.randint(1, total)
    cumulative = 0
    for coin in COIN_TYPES:
        cumulative += coin["weight"]
        if r <= cumulative:
            return coin
    return COIN_TYPES[0]


class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 100
        self.speed = PLAYER_SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.width, self.height), border_radius=6)
        pygame.draw.rect(surface, (150, 210, 255), (self.x + 6, self.y + 8, self.width - 12, 14), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.x - 6, self.y + 6, 8, 14), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.x + self.width - 2, self.y + 6, 8, 14), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.x - 6, self.y + 40, 8, 14), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.x + self.width - 2, self.y + 40, 8, 14), border_radius=3)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > ROAD_LEFT:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.width < ROAD_RIGHT:
            self.x += self.speed


class Enemy:
    def __init__(self, speed):
        self.width = 40
        self.height = 60
        self.x = random.randint(ROAD_LEFT, ROAD_RIGHT - self.width)
        self.y = -self.height
        self.speed = speed

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.x, self.y, self.width, self.height), border_radius=6)
        pygame.draw.rect(surface, (255, 150, 150), (self.x + 6, self.y + 8, self.width - 12, 14), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.x - 6, self.y + 6, 8, 14), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.x + self.width - 2, self.y + 6, 8, 14), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.x - 6, self.y + 40, 8, 14), border_radius=3)
        pygame.draw.rect(surface, BLACK, (self.x + self.width - 2, self.y + 40, 8, 14), border_radius=3)

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Coin:
    def __init__(self):
        coin_type = pick_coin_type()
        self.color = coin_type["color"]
        self.points = coin_type["points"]
        self.radius = 10 + (coin_type["points"] - 1) * 3  # bigger = more points
        self.x = random.randint(ROAD_LEFT + self.radius, ROAD_RIGHT - self.radius)
        self.y = -self.radius
        self.speed = COIN_SPEED_BASE

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, WHITE, (self.x, self.y), self.radius, 2)
        label = small_font.render(str(self.points), True, BLACK)
        surface.blit(label, (self.x - label.get_width() // 2, self.y - label.get_height() // 2))

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)


def draw_road(surface, offset):
    """Draw road with moving lane markings."""
    surface.fill(DARK_GRAY)
    pygame.draw.rect(surface, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
    pygame.draw.line(surface, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 3)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 3)
    dash_height = 40
    gap = 30
    total = dash_height + gap
    center_x = (ROAD_LEFT + ROAD_RIGHT) // 2
    for i in range(-1, HEIGHT // total + 2):
        y = i * total + (offset % total)
        pygame.draw.rect(surface, LINE_COLOR, (center_x - 3, y, 6, dash_height))


def draw_hud(surface, score, coins, enemy_speed_level):
    """Draw score and speed info."""
    score_text = font.render(f"Score: {score}", True, WHITE)
    surface.blit(score_text, (10, 10))
    coins_text = small_font.render(f"Coins: {coins}", True, YELLOW)
    surface.blit(coins_text, (10, 50))
    next_speedup = N_COINS_FOR_SPEEDUP - (coins % N_COINS_FOR_SPEEDUP)
    speed_text = small_font.render(f"Enemy Lv: {enemy_speed_level}  Next boost in {next_speedup} coins", True, ORANGE)
    surface.blit(speed_text, (10, 70))


def game_over_screen(surface, score):
    """Show game over and wait for restart."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    go_text = font.render("GAME OVER", True, RED)
    sc_text = font.render(f"Score: {score}", True, WHITE)
    restart_text = small_font.render("Press R to restart or Q to quit", True, GRAY)

    surface.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 60))
    surface.blit(sc_text, (WIDTH // 2 - sc_text.get_width() // 2, HEIGHT // 2 - 10))
    surface.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


def main():
    player = Player()
    enemies = []
    coins = []
    score = 0
    coin_count = 0
    road_offset = 0
    enemy_speed = ENEMY_SPEED_BASE
    enemy_speed_level = 1

    enemy_timer = 0
    coin_timer = 0
    ENEMY_SPAWN_INTERVAL = 90   # frames
    COIN_SPAWN_INTERVAL = 60    # frames

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.move(keys)

        enemy_timer += 1
        if enemy_timer >= ENEMY_SPAWN_INTERVAL:
            enemies.append(Enemy(enemy_speed))
            enemy_timer = 0

        coin_timer += 1
        if coin_timer >= COIN_SPAWN_INTERVAL:
            coins.append(Coin())
            coin_timer = 0

        for enemy in enemies[:]:
            enemy.update()
            if enemy.y > HEIGHT:
                enemies.remove(enemy)
            elif player.get_rect().colliderect(enemy.get_rect()):
                game_over_screen(screen, score)
                main()
                return

        for coin in coins[:]:
            coin.update()
            if coin.y > HEIGHT:
                coins.remove(coin)
            elif player.get_rect().colliderect(coin.get_rect()):
                score += coin.points
                coin_count += 1
                coins.remove(coin)
                # Speed up enemy every N coins collected
                if coin_count % N_COINS_FOR_SPEEDUP == 0:
                    enemy_speed += 1
                    enemy_speed_level += 1

        road_offset += 5

        draw_road(screen, road_offset)
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for coin in coins:
            coin.draw(screen)
        draw_hud(screen, score, coin_count, enemy_speed_level)

        pygame.display.flip()


if __name__ == "__main__":
    main()