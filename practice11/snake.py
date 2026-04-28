import pygame
import random
import sys
import time

pygame.init()

WIDTH, HEIGHT = 400, 400
CELL = 20
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT + 60))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 180, 50)
DARK_GREEN = (30, 120, 30)
RED = (220, 50, 50)
YELLOW = (255, 215, 0)
SILVER = (192, 192, 192)
BLUE = (100, 180, 255)
GRAY = (80, 80, 80)
BG = (20, 20, 20)
HUD_BG = (30, 30, 30)

# Food types: (weight, color, points, lifetime_seconds)
# lifetime=None means it never disappears
FOOD_TYPES = [
    {"weight": 50, "color": RED,    "points": 1, "lifetime": None},   # common, permanent
    {"weight": 30, "color": YELLOW, "points": 2, "lifetime": 8.0},    # bonus, disappears in 8s
    {"weight": 20, "color": BLUE,   "points": 5, "lifetime": 5.0},    # rare, disappears in 5s
]


def pick_food_type():
    """Weighted random food type selection."""
    total = sum(f["weight"] for f in FOOD_TYPES)
    r = random.randint(1, total)
    cumulative = 0
    for food in FOOD_TYPES:
        cumulative += food["weight"]
        if r <= cumulative:
            return food
    return FOOD_TYPES[0]


class Food:
    def __init__(self, snake_body):
        food_type = pick_food_type()
        self.color = food_type["color"]
        self.points = food_type["points"]
        self.lifetime = food_type["lifetime"]
        self.spawn_time = time.time()
        self.pos = self._random_pos(snake_body)

    def _random_pos(self, snake_body):
        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
            if pos not in snake_body:
                return pos

    def is_expired(self):
        """Check if food has exceeded its lifetime."""
        if self.lifetime is None:
            return False
        return time.time() - self.spawn_time > self.lifetime

    def time_left(self):
        """Seconds remaining (for display)."""
        if self.lifetime is None:
            return None
        return max(0, self.lifetime - (time.time() - self.spawn_time))

    def draw(self, surface):
        x = self.pos[0] * CELL + CELL // 2
        y = self.pos[1] * CELL + CELL // 2
        radius = CELL // 2 - 2
        pygame.draw.circle(surface, self.color, (x, y), radius)
        pygame.draw.circle(surface, WHITE, (x, y), radius, 1)

        if self.lifetime is not None:
            t = self.time_left()
            ratio = t / self.lifetime
            bar_w = CELL - 4
            bar_h = 3
            bx = self.pos[0] * CELL + 2
            by = self.pos[1] * CELL - 4
            pygame.draw.rect(surface, GRAY, (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, self.color, (bx, by, int(bar_w * ratio), bar_h))

        label = small_font.render(str(self.points), True, BLACK)
        surface.blit(label, (x - label.get_width() // 2, y - label.get_height() // 2))


class Snake:
    def __init__(self):
        start = (COLS // 2, ROWS // 2)
        self.body = [start, (start[0] - 1, start[1]), (start[0] - 2, start[1])]
        self.direction = (1, 0)
        self.grow = False

    def change_direction(self, new_dir):
        # Prevent reversing
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # Wall collision → game over signal
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            return False
        if new_head in self.body:
            return False

        self.body.insert(0, new_head)
        if self.grow:
            self.grow = False
        else:
            self.body.pop()
        return True

    def eat(self):
        self.grow = True

    def draw(self, surface):
        for i, segment in enumerate(self.body):
            x = segment[0] * CELL
            y = segment[1] * CELL
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(surface, color, (x + 1, y + 1, CELL - 2, CELL - 2), border_radius=4)
            if i == 0:
                ex = x + CELL - 5 if self.direction[0] >= 0 else x + 3
                ey = y + 4
                pygame.draw.circle(surface, WHITE, (ex, ey), 3)
                pygame.draw.circle(surface, BLACK, (ex, ey), 1)


def draw_hud(surface, score, length):
    pygame.draw.rect(surface, HUD_BG, (0, HEIGHT, WIDTH, 60))
    score_text = font.render(f"Score: {score}", True, WHITE)
    len_text = small_font.render(f"Length: {length}", True, GRAY)
    surface.blit(score_text, (10, HEIGHT + 10))
    surface.blit(len_text, (10, HEIGHT + 38))


def game_over_screen(surface, score):
    overlay = pygame.Surface((WIDTH, HEIGHT + 60), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    go = font.render("GAME OVER", True, RED)
    sc = font.render(f"Score: {score}", True, WHITE)
    restart = small_font.render("R - restart   Q - quit", True, GRAY)

    surface.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT // 2 - 50))
    surface.blit(sc, (WIDTH // 2 - sc.get_width() // 2, HEIGHT // 2))
    surface.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()


def main():
    snake = Snake()
    foods = [Food(snake.body)]  # Start with one food
    score = 0
    move_timer = 0
    MOVE_INTERVAL = 8  # frames between snake moves (lower = faster)

    food_spawn_timer = 0
    FOOD_SPAWN_INTERVAL = 300  # spawn extra food every ~5 seconds

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))

        move_timer += 1
        if move_timer >= MOVE_INTERVAL:
            move_timer = 0
            if not snake.move():
                if game_over_screen(screen, score):
                    main()
                    return

        head = snake.body[0]
        for food in foods[:]:
            if head == food.pos:
                score += food.points
                snake.eat()
                foods.remove(food)
                foods.append(Food(snake.body))

        for food in foods[:]:
            if food.is_expired():
                foods.remove(food)

        # Make sure there's always at least one food
        if not foods:
            foods.append(Food(snake.body))

        food_spawn_timer += 1
        if food_spawn_timer >= FOOD_SPAWN_INTERVAL and len(foods) < 4:
            foods.append(Food(snake.body))
            food_spawn_timer = 0

        screen.fill(BG)
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, (30, 30, 30), (0, y), (WIDTH, y))

        for food in foods:
            food.draw(screen)
        snake.draw(screen)
        draw_hud(screen, score, len(snake.body))

        pygame.display.flip()


if __name__ == "__main__":
    main()