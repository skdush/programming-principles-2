import pygame
import random
import time

WIDTH, HEIGHT = 400, 600
ROAD_LEFT  = 60
ROAD_RIGHT = 340
ROAD_W     = ROAD_RIGHT - ROAD_LEFT
FPS        = 60

BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (60,  60,  60)
GREEN   = (34,  139, 34)
YELLOW  = (255, 215, 0)
RED     = (220, 50,  50)
ORANGE  = (255, 140, 0)
BLUE    = (50,  100, 220)
PURPLE  = (160, 30,  200)
TEAL    = (0,   180, 160)
DARK    = (20,  20,  20)
HUD_BG  = (30,  30,  30)

DIFF_PARAMS = {
    "easy":   {"enemy_int": 120, "obs_int": 180, "base_speed": 4},
    "normal": {"enemy_int": 80,  "obs_int": 120, "base_speed": 5},
    "hard":   {"enemy_int": 50,  "obs_int": 80,  "base_speed": 7},
}
COIN_TYPES = [
    {"weight": 50, "color": YELLOW,           "points": 1},
    {"weight": 30, "color": (192, 192, 192),  "points": 2},
    {"weight": 20, "color": (100, 200, 255),  "points": 5},
]
POWERUP_TIMEOUT = 8.0


def _pick_coin():
    total = sum(c["weight"] for c in COIN_TYPES)
    r = random.randint(1, total)
    s = 0
    for c in COIN_TYPES:
        s += c["weight"]
        if r <= s:
            return c
    return COIN_TYPES[0]


def _draw_car(surface, rect, color):
    pygame.draw.rect(surface, color, rect, border_radius=6)
    win = pygame.Rect(rect.x + 7, rect.y + 9, rect.width - 14, 18)
    pygame.draw.rect(surface, (160, 210, 255), win, border_radius=3)
    for wx, wy in [
        (rect.x - 6,         rect.y + 7),
        (rect.right - 4,     rect.y + 7),
        (rect.x - 6,         rect.bottom - 23),
        (rect.right - 4,     rect.bottom - 23),
    ]:
        pygame.draw.rect(surface, BLACK, (wx, wy, 10, 16), border_radius=3)


class Player:
    W, H = 40, 66

    def __init__(self, color):
        self.color  = tuple(color)
        self.x      = WIDTH // 2 - self.W // 2
        self.y      = HEIGHT - 110
        self.speed  = 6
        self.shield = False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > ROAD_LEFT + 2:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x + self.W < ROAD_RIGHT - 2:
            self.x += self.speed

    def draw(self, surface):
        _draw_car(surface, self.rect(), self.color)
        if self.shield:
            pygame.draw.ellipse(surface, (80, 200, 255),
                                self.rect().inflate(12, 12), 3)


class Enemy:
    W, H = 40, 66
    COLORS = [(200, 50, 50), (50, 180, 50), (200, 130, 50), (180, 50, 200)]

    def __init__(self, speed):
        self.x     = random.randint(ROAD_LEFT + 2, ROAD_RIGHT - self.W - 2)
        self.y     = -self.H
        self.speed = speed
        self.color = random.choice(self.COLORS)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        _draw_car(surface, self.rect(), self.color)


class Coin:
    def __init__(self, speed):
        ct        = _pick_coin()
        self.color  = ct["color"]
        self.points = ct["points"]
        self.radius = 10 + (ct["points"] - 1) * 3
        self.x    = random.randint(ROAD_LEFT + self.radius, ROAD_RIGHT - self.radius)
        self.y    = -self.radius
        self.speed = speed

    def rect(self):
        r = self.radius
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def update(self):
        self.y += self.speed

    def draw(self, surface, font):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, WHITE, (self.x, self.y), self.radius, 2)
        lbl = font.render(str(self.points), True, BLACK)
        surface.blit(lbl, (self.x - lbl.get_width() // 2, self.y - lbl.get_height() // 2))


class Obstacle:
    TYPES = [
        {"name": "barrier",   "w": 50, "h": 18, "color": (140, 100, 50)},
        {"name": "pothole",   "w": 28, "h": 28, "color": (40,  40,  40)},
        {"name": "oil_spill", "w": 44, "h": 22, "color": (20,  20,  80)},
    ]

    def __init__(self, speed):
        t        = random.choice(self.TYPES)
        self.w   = t["w"]
        self.h   = t["h"]
        self.color = t["color"]
        self.name  = t["name"]
        self.x   = random.randint(ROAD_LEFT + 4, ROAD_RIGHT - self.w - 4)
        self.y   = -self.h
        self.speed = speed
        self.slow_factor = 0.5 if self.name == "oil_spill" else 1.0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        r = self.rect()
        if self.name == "barrier":
            pygame.draw.rect(surface, self.color, r, border_radius=4)
            pygame.draw.rect(surface, WHITE, r, 2, border_radius=4)
        elif self.name == "pothole":
            pygame.draw.ellipse(surface, self.color, r)
            pygame.draw.ellipse(surface, (80, 80, 80), r, 2)
        else:
            pygame.draw.ellipse(surface, self.color, r)


class PowerUpItem:
    TYPES = {
        "nitro":  {"color": ORANGE, "label": "N"},
        "shield": {"color": TEAL,   "label": "S"},
        "repair": {"color": GREEN,  "label": "R"},
    }

    def __init__(self, speed):
        self.ptype = random.choice(list(self.TYPES.keys()))
        cfg        = self.TYPES[self.ptype]
        self.color = cfg["color"]
        self.label = cfg["label"]
        self.x     = random.randint(ROAD_LEFT + 16, ROAD_RIGHT - 16)
        self.y     = -16
        self.radius = 16
        self.speed  = speed
        self.spawn_t = time.time()

    def is_expired(self):
        return time.time() - self.spawn_t > POWERUP_TIMEOUT

    def rect(self):
        r = self.radius
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def update(self):
        self.y += self.speed

    def draw(self, surface, font):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, WHITE,       (self.x, self.y), self.radius, 2)
        lbl = font.render(self.label, True, BLACK)
        surface.blit(lbl, (self.x - lbl.get_width() // 2, self.y - lbl.get_height() // 2))


class NitroStrip:
    def __init__(self, speed):
        lane_w = ROAD_W // 3
        lane   = random.randint(0, 2)
        self.x = ROAD_LEFT + lane * lane_w + 4
        self.w = lane_w - 8
        self.h = 14
        self.y = -self.h
        self.speed = speed

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        r = self.rect()
        pygame.draw.rect(surface, ORANGE, r, border_radius=3)
        pygame.draw.rect(surface, YELLOW, r, 2, border_radius=3)


class Game:
    def __init__(self, settings):
        self.diff   = settings.get("difficulty", "normal")
        self.dp     = DIFF_PARAMS[self.diff]
        self.player = Player(settings["car_color"])

        self.enemies    = []
        self.coins      = []
        self.obstacles  = []
        self.powerups   = []
        self.strips     = []

        self.score        = 0
        self.coin_count   = 0
        self.distance     = 0
        self.road_offset  = 0
        self.enemy_speed  = self.dp["base_speed"]
        self.speed_level  = 1

        self.active_pu    = None
        self.pu_end_time  = 0
        self.slow_until   = 0

        self.game_over = False

        self.enemy_t  = 0
        self.coin_t   = 0
        self.obs_t    = 0
        self.pu_t     = 0
        self.strip_t  = 0
        self.coins_for_speedup = 5

        self.small_f = pygame.font.SysFont("Arial", 18, bold=True)
        self.big_f   = pygame.font.SysFont("Arial", 26, bold=True)

    def _safe_spawn(self, new_rect):
        pr = self.player.rect().inflate(60, 80)
        return not new_rect.colliderect(pr)

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys)

        now = time.time()
        if self.active_pu == "nitro":
            self.player.speed = 10
        elif self.active_pu == "slow_field":
            self.player.speed = 3
        else:
            self.player.speed = 6

        if self.active_pu and now > self.pu_end_time and self.active_pu != "shield":
            self.active_pu = None

        spd = self.enemy_speed
        self.road_offset = (self.road_offset + spd) % (HEIGHT + 1)
        self.distance    += spd

        self.enemy_t += 1
        if self.enemy_t >= self.dp["enemy_int"]:
            e = Enemy(spd)
            if self._safe_spawn(e.rect()):
                self.enemies.append(e)
            self.enemy_t = 0

        self.coin_t += 1
        if self.coin_t >= 55:
            self.coins.append(Coin(spd))
            self.coin_t = 0

        self.obs_t += 1
        if self.obs_t >= self.dp["obs_int"]:
            o = Obstacle(spd)
            if self._safe_spawn(o.rect()):
                self.obstacles.append(o)
            self.obs_t = 0

        self.pu_t += 1
        if self.pu_t >= 200:
            p = PowerUpItem(spd)
            if self._safe_spawn(p.rect()):
                self.powerups.append(p)
            self.pu_t = 0

        self.strip_t += 1
        if self.strip_t >= 250:
            self.strips.append(NitroStrip(spd))
            self.strip_t = 0

        pr = self.player.rect()

        for e in self.enemies[:]:
            e.update()
            if e.y > HEIGHT:
                self.enemies.remove(e)
                self.score += 5
            elif pr.colliderect(e.rect()):
                if self.active_pu == "shield":
                    self.active_pu = None
                    self.enemies.remove(e)
                else:
                    self.game_over = True
                    return

        for c in self.coins[:]:
            c.update()
            if c.y > HEIGHT:
                self.coins.remove(c)
            elif pr.colliderect(c.rect()):
                self.score      += c.points * 10
                self.coin_count += c.points
                self.coins.remove(c)
                if self.coin_count // self.coins_for_speedup >= self.speed_level:
                    self.enemy_speed += 1
                    self.speed_level += 1

        for o in self.obstacles[:]:
            o.update()
            if o.y > HEIGHT:
                self.obstacles.remove(o)
            elif pr.colliderect(o.rect()):
                if o.name == "oil_spill":
                    self.slow_until = now + 2.0
                    self.obstacles.remove(o)
                elif self.active_pu == "repair":
                    self.active_pu = None
                    self.obstacles.remove(o)
                elif self.active_pu == "shield":
                    self.active_pu = None
                    self.obstacles.remove(o)
                else:
                    self.game_over = True
                    return

        if now < self.slow_until:
            self.player.speed = 3

        for p in self.powerups[:]:
            p.update()
            if p.y > HEIGHT or p.is_expired():
                self.powerups.remove(p)
            elif pr.colliderect(p.rect()):
                self._apply_powerup(p.ptype, now)
                self.powerups.remove(p)

        for s in self.strips[:]:
            s.update()
            if s.y > HEIGHT:
                self.strips.remove(s)
            elif pr.colliderect(s.rect()):
                if self.active_pu is None:
                    self.active_pu   = "nitro"
                    self.pu_end_time = now + 3.0
                self.strips.remove(s)

        self.score += spd // 10

    def _apply_powerup(self, ptype, now):
        if ptype == "nitro":
            self.active_pu   = "nitro"
            self.pu_end_time = now + 4.0
        elif ptype == "shield":
            self.active_pu     = "shield"
            self.player.shield = True
            self.pu_end_time   = now + 9999
        elif ptype == "repair":
            self.active_pu   = "repair"
            self.pu_end_time = now + 1.0
            self.score       += 30

    def draw(self, surface):
        surface.fill((20, 20, 20))
        self._draw_road(surface)
        for s in self.strips:
            s.draw(surface)
        for o in self.obstacles:
            o.draw(surface)
        for c in self.coins:
            c.draw(surface, self.small_f)
        for p in self.powerups:
            p.draw(surface, self.small_f)
        for e in self.enemies:
            e.draw(surface)
        self.player.draw(surface)
        self._draw_hud(surface)

    def _draw_road(self, surface):
        pygame.draw.rect(surface, GRAY, (ROAD_LEFT, 0, ROAD_W, HEIGHT))
        pygame.draw.line(surface, WHITE, (ROAD_LEFT,  0), (ROAD_LEFT,  HEIGHT), 3)
        pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 3)
        dash_h, gap = 40, 30
        total = dash_h + gap
        cx    = WIDTH // 2
        for i in range(-1, HEIGHT // total + 2):
            y = i * total + (self.road_offset % total)
            pygame.draw.rect(surface, YELLOW, (cx - 3, int(y), 6, dash_h))

    def _draw_hud(self, surface):
        pygame.draw.rect(surface, HUD_BG, (0, 0, 60, HEIGHT))
        labels = [
            (f"Score",       str(self.score),            40),
            (f"Coins",       str(self.coin_count),       100),
            (f"Dist",        f"{self.distance // 10}m",  160),
            (f"Lv",          str(self.speed_level),      220),
        ]
        for lbl, val, y in labels:
            l1 = self.small_f.render(lbl, True, GRAY)
            l2 = self.small_f.render(val, True, WHITE)
            surface.blit(l1, (5, y))
            surface.blit(l2, (5, y + 20))

        if self.active_pu:
            now     = time.time()
            remain  = max(0, self.pu_end_time - now)
            pu_cols = {"nitro": ORANGE, "shield": TEAL, "repair": GREEN}
            col     = pu_cols.get(self.active_pu, WHITE)
            pu_lbl  = self.small_f.render(self.active_pu.upper(), True, col)
            surface.blit(pu_lbl, (5, 300))
            if self.active_pu != "shield":
                t_lbl = self.small_f.render(f"{remain:.1f}s", True, col)
                surface.blit(t_lbl, (5, 320))
