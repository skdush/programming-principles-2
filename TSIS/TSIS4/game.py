import pygame
import random
import time

CELL  = 20
COLS  = 30
ROWS  = 25
GAME_W = COLS * CELL
GAME_H = ROWS * CELL
HUD_H  = 50
WIDTH  = GAME_W
HEIGHT = GAME_H + HUD_H

WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GRAY       = (40,  40,  40)
WALL_COL   = (100, 100, 100)
RED        = (220, 50,  50)
POISON_COL = (160, 0,   0)
YELLOW     = (255, 215, 0)
ORANGE     = (255, 140, 0)
TEAL       = (0,   180, 160)
BLUE       = (80,  150, 255)
HUD_BG     = (25,  25,  25)

FOODS_PER_LEVEL  = 5
BASE_INTERVAL    = 160
PU_TIMEOUT_MS    = 8000
OBSTACLE_LEVEL   = 3
OBSTACLES_COUNT  = 6


def _rnd_cell(exclude):
    while True:
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos not in exclude:
            return pos


def _gen_obstacles(snake, food_pos, existing_pu):
    blocked = set(snake) | {food_pos} | (existing_pu or set())
    walls = set()
    attempts = 0
    while len(walls) < OBSTACLES_COUNT and attempts < 500:
        attempts += 1
        x = random.randint(2, COLS - 3)
        y = random.randint(2, ROWS - 3)
        pos = (x, y)
        if pos in blocked or pos in walls:
            continue
        head = snake[0]
        if abs(x - head[0]) <= 3 and abs(y - head[1]) <= 3:
            continue
        walls.add(pos)
    return walls


class Game:
    def __init__(self, username, settings, personal_best=0):
        self.username     = username
        self.settings     = settings
        self.personal_best = personal_best

        cx, cy = COLS // 2, ROWS // 2
        self.snake     = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_dir  = (1, 0)

        self.food      = _rnd_cell(set(self.snake))
        self.poison    = None
        self.powerup   = None
        self.pu_type   = None
        self.pu_spawn  = 0
        self.obstacles = set()

        self.score       = 0
        self.level       = 1
        self.foods_eaten = 0
        self.move_int    = BASE_INTERVAL
        self.move_timer  = 0
        self.game_over   = False

        self.active_pu    = None
        self.pu_end_ticks = 0
        self.shield_used  = False

        self.poison_timer  = 0
        self.POISON_INT    = 8000
        self.pu_item_timer = 0
        self.PU_ITEM_INT   = 6000

        self.snake_color = tuple(settings.get("snake_color", [50, 200, 50]))
        self.grid_on     = settings.get("grid_overlay", True)

        self.font_big  = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_sm   = pygame.font.SysFont("Arial", 17)

    def _all_blocked(self):
        blocked = set(self.snake)
        if self.food:
            blocked.add(self.food)
        if self.poison:
            blocked.add(self.poison)
        if self.powerup:
            blocked.add(self.powerup)
        blocked |= self.obstacles
        return blocked

    def handle_key(self, key):
        dirs = {
            pygame.K_UP:    (0, -1),
            pygame.K_DOWN:  (0,  1),
            pygame.K_LEFT:  (-1, 0),
            pygame.K_RIGHT: (1,  0),
        }
        nd = dirs.get(key)
        if nd and (nd[0] * -1, nd[1] * -1) != self.direction:
            self.next_dir = nd

    def update(self, dt):
        if self.game_over:
            return

        now = pygame.time.get_ticks()

        if self.active_pu == "shield" and self.shield_used:
            self.active_pu = None
            self.shield_used = False

        if self.active_pu in ("speed", "slow") and now > self.pu_end_ticks:
            self.active_pu = None
            self.move_int  = max(40, BASE_INTERVAL - (self.level - 1) * 15)

        self.poison_timer += dt
        if self.poison_timer >= self.POISON_INT and self.poison is None:
            self.poison = _rnd_cell(self._all_blocked())
            self.poison_timer = 0

        self.pu_item_timer += dt
        if self.pu_item_timer >= self.PU_ITEM_INT and self.powerup is None:
            self.powerup  = _rnd_cell(self._all_blocked())
            self.pu_type  = random.choice(["speed", "slow", "shield"])
            self.pu_spawn = now
            self.pu_item_timer = 0

        if self.powerup and now - self.pu_spawn > PU_TIMEOUT_MS:
            self.powerup = None
            self.pu_type = None

        self.move_timer += dt
        if self.move_timer < self.move_int:
            return
        self.move_timer = 0

        self.direction = self.next_dir
        hx, hy = self.snake[0]
        nx, ny = hx + self.direction[0], hy + self.direction[1]

        if nx <= 0 or nx >= COLS - 1 or ny <= 0 or ny >= ROWS - 1:
            if self.active_pu == "shield":
                self.shield_used = True
                nx = max(1, min(COLS - 2, nx))
                ny = max(1, min(ROWS - 2, ny))
            else:
                self.game_over = True
                return

        if (nx, ny) in self.snake:
            if self.active_pu == "shield":
                self.shield_used = True
            else:
                self.game_over = True
                return

        if (nx, ny) in self.obstacles:
            if self.active_pu == "shield":
                self.shield_used = True
            else:
                self.game_over = True
                return

        self.snake.insert(0, (nx, ny))

        if (nx, ny) == self.food:
            self.score      += 10
            self.foods_eaten += 1
            self.food = _rnd_cell(self._all_blocked())
            if self.foods_eaten % FOODS_PER_LEVEL == 0:
                self.level   += 1
                self.move_int = max(40, BASE_INTERVAL - (self.level - 1) * 15)
                if self.level >= OBSTACLE_LEVEL:
                    self.obstacles = _gen_obstacles(
                        self.snake, self.food, self.powerup)
        elif (nx, ny) == self.poison:
            trim = min(2, len(self.snake) - 1)
            self.snake = self.snake[:-trim] if trim > 0 else self.snake
            self.poison = None
            if len(self.snake) <= 1:
                self.game_over = True
                return
        elif (nx, ny) == self.powerup:
            self._activate_pu(now)
            self.powerup = None
            self.pu_type = None
        else:
            self.snake.pop()

    def _activate_pu(self, now):
        if self.pu_type == "speed":
            self.active_pu    = "speed"
            self.pu_end_ticks = now + 5000
            self.move_int     = max(25, self.move_int // 2)
        elif self.pu_type == "slow":
            self.active_pu    = "slow"
            self.pu_end_ticks = now + 5000
            self.move_int     = min(300, self.move_int * 2)
        elif self.pu_type == "shield":
            self.active_pu   = "shield"
            self.shield_used = False

    def draw(self, surface):
        surface.fill(GRAY)
        pygame.draw.rect(surface, BLACK, (0, 0, GAME_W, GAME_H))

        if self.grid_on:
            for gx in range(0, GAME_W, CELL):
                pygame.draw.line(surface, (30, 30, 30), (gx, 0), (gx, GAME_H))
            for gy in range(0, GAME_H, CELL):
                pygame.draw.line(surface, (30, 30, 30), (0, gy), (GAME_W, gy))

        for x in range(COLS):
            pygame.draw.rect(surface, WALL_COL, (x * CELL, 0, CELL, CELL))
            pygame.draw.rect(surface, WALL_COL, (x * CELL, (ROWS-1)*CELL, CELL, CELL))
        for y in range(1, ROWS - 1):
            pygame.draw.rect(surface, WALL_COL, (0, y*CELL, CELL, CELL))
            pygame.draw.rect(surface, WALL_COL, ((COLS-1)*CELL, y*CELL, CELL, CELL))

        for obs in self.obstacles:
            ox, oy = obs
            pygame.draw.rect(surface, (80, 80, 80),
                             (ox*CELL+1, oy*CELL+1, CELL-2, CELL-2), border_radius=3)
            pygame.draw.rect(surface, (140, 140, 140),
                             (ox*CELL+1, oy*CELL+1, CELL-2, CELL-2), 2, border_radius=3)

        if self.food:
            fx, fy = self.food
            pygame.draw.circle(surface, RED,
                               (fx*CELL + CELL//2, fy*CELL + CELL//2), CELL//2 - 2)

        if self.poison:
            px, py = self.poison
            pygame.draw.circle(surface, POISON_COL,
                               (px*CELL + CELL//2, py*CELL + CELL//2), CELL//2 - 2)
            pygame.draw.circle(surface, (255, 80, 80),
                               (px*CELL + CELL//2, py*CELL + CELL//2), CELL//2 - 2, 2)

        if self.powerup:
            pux, puy = self.powerup
            pu_cols = {"speed": ORANGE, "slow": BLUE, "shield": TEAL}
            col = pu_cols.get(self.pu_type, YELLOW)
            pygame.draw.rect(surface, col,
                             (pux*CELL+2, puy*CELL+2, CELL-4, CELL-4), border_radius=4)
            now = pygame.time.get_ticks()
            ratio = max(0, 1 - (now - self.pu_spawn) / PU_TIMEOUT_MS)
            pygame.draw.rect(surface, WHITE,
                             (pux*CELL+2, puy*CELL+2, int((CELL-4)*ratio), 3))

        dark_green = tuple(max(0, c - 60) for c in self.snake_color)
        for i, (sx, sy) in enumerate(self.snake):
            col = self.snake_color if i == 0 else dark_green
            pygame.draw.rect(surface, col,
                             (sx*CELL+1, sy*CELL+1, CELL-2, CELL-2), border_radius=4)
        if self.active_pu == "shield":
            hx, hy = self.snake[0]
            pygame.draw.ellipse(surface, TEAL,
                                pygame.Rect(hx*CELL-3, hy*CELL-3, CELL+6, CELL+6), 2)

        self._draw_hud(surface)

    def _draw_hud(self, surface):
        pygame.draw.rect(surface, HUD_BG, (0, GAME_H, WIDTH, HUD_H))
        s_lbl  = self.font_big.render(f"Score: {self.score}", True, WHITE)
        lv_lbl = self.font_big.render(f"Lv: {self.level}", True, YELLOW)
        pb_lbl = self.font_sm.render(f"Best: {self.personal_best}", True, (160, 160, 160))
        surface.blit(s_lbl,  (8,  GAME_H + 6))
        surface.blit(lv_lbl, (WIDTH//2 - lv_lbl.get_width()//2, GAME_H + 6))
        surface.blit(pb_lbl, (WIDTH - pb_lbl.get_width() - 8, GAME_H + 28))

        if self.active_pu:
            now = pygame.time.get_ticks()
            pu_cols = {"speed": ORANGE, "slow": BLUE, "shield": TEAL}
            col = pu_cols.get(self.active_pu, WHITE)
            pu_lbl = self.font_sm.render(self.active_pu.upper(), True, col)
            surface.blit(pu_lbl, (WIDTH - pu_lbl.get_width() - 8, GAME_H + 6))
            if self.active_pu in ("speed", "slow"):
                remain = max(0, (self.pu_end_ticks - now) / 1000)
                t_lbl  = self.font_sm.render(f"{remain:.1f}s", True, col)
                surface.blit(t_lbl, (WIDTH - t_lbl.get_width() - 8, GAME_H + 6))
