import pygame, random
from config import W, H, CS, load_settings

class SnakeGame:
    def __init__(self, username, pb):
        self.settings = load_settings()
        self.username = username
        self.pb = pb

        self.zmeika = [[15, 10], [14, 10]]
        self.dx, self.dy = 1, 0
        self.ndx, self.ndy = 1, 0

        self.sc = 0
        self.lvl = 1

        self.obstacles = []
        self.eda = self.make_eda()
        self.poison = self.make_poison()

        self.powerup = None
        self.powerup_spawn_time = 0
        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield_active = False

        self.game_over = False

    def is_free(self, x, y):
        return [x, y] not in self.zmeika and [x, y] not in self.obstacles

    def make_eda(self):
        while True:
            x, y = random.randint(0, W - 1), random.randint(0, H - 1)
            if self.is_free(x, y):
                weight = random.choice([1, 1, 3])
                timer = 100 if weight == 1 else 50
                return [x, y, weight, timer]

    def make_poison(self):
        if random.random() < 0.3:
            while True:
                x, y = random.randint(0, W - 1), random.randint(0, H - 1)
                if self.is_free(x, y) and [x, y] != self.eda[:2]:
                    return [x, y]
        return None

    def make_powerup(self):
        while True:
            x, y = random.randint(0, W - 1), random.randint(0, H - 1)
            if self.is_free(x, y) and [x, y] != self.eda[:2] and [x, y] != self.poison:
                type_ = random.choice(["speed", "slow", "shield"])
                return [x, y, type_]

    def spawn_obstacles(self):
        self.obstacles = []
        if self.lvl >= 3:
            for _ in range(self.lvl * 2):
                while True:
                    x, y = random.randint(0, W - 1), random.randint(0, H - 1)
                    if self.is_free(x, y) and [x, y] != self.eda[:2]:
                        self.obstacles.append([x, y])
                        break

    def update(self):
        if self.game_over: return

        self.dx, self.dy = self.ndx, self.ndy
        nx, ny = self.zmeika[0][0] + self.dx, self.zmeika[0][1] + self.dy

        current_time = pygame.time.get_ticks()

        hit_wall = nx < 0 or nx >= W or ny < 0 or ny >= H
        hit_self = [nx, ny] in self.zmeika
        hit_obs = [nx, ny] in self.obstacles

        if hit_wall or hit_self or hit_obs:
            if self.shield_active:
                self.shield_active = False
                return
            else:
                self.game_over = True
                return

        self.zmeika.insert(0, [nx, ny])
        ate_something = False

        self.eda[3] -= 1
        if self.eda[3] <= 0:
            self.eda = self.make_eda()

        if nx == self.eda[0] and ny == self.eda[1]:
            self.sc += self.eda[2]
            if self.sc // 4 + 1 > self.lvl:
                self.lvl += 1
                self.spawn_obstacles()
            self.eda = self.make_eda()
            self.poison = self.make_poison()
            ate_something = True

            if not self.powerup and random.random() < 0.2:
                self.powerup = self.make_powerup()
                self.powerup_spawn_time = current_time

        elif self.poison and nx == self.poison[0] and ny == self.poison[1]:
            if len(self.zmeika) <= 3:
                self.game_over = True
                return
            self.zmeika.pop()
            self.zmeika.pop()
            self.zmeika.pop()
            self.poison = None
            ate_something = True

        elif self.powerup and nx == self.powerup[0] and ny == self.powerup[1]:
            self.active_powerup = self.powerup[2]
            self.powerup_end_time = current_time + 5000
            if self.active_powerup == "shield":
                self.shield_active = True
            self.powerup = None
            self.zmeika.pop()
            ate_something = True

        if not ate_something:
            self.zmeika.pop()

        if self.powerup and current_time - self.powerup_spawn_time > 8000:
            self.powerup = None

        if self.active_powerup in ["speed", "slow"] and current_time > self.powerup_end_time:
            self.active_powerup = None

    def get_speed(self):
        base = 8 + (self.lvl * 2)
        if self.active_powerup == "speed": return base + 8
        if self.active_powerup == "slow": return max(4, base - 6)
        return base

    def draw(self, screen):
        screen.fill((0, 0, 0))

        if self.settings["grid_overlay"]:
            for x in range(0, W * CS, CS): pygame.draw.line(screen, (30, 30, 30), (x, 0), (x, H * CS))
            for y in range(0, H * CS, CS): pygame.draw.line(screen, (30, 30, 30), (0, y), (W * CS, y))

        eda_color = (255, 0, 0) if self.eda[2] == 1 else (0, 150, 255)
        pygame.draw.rect(screen, eda_color, (self.eda[0] * CS, self.eda[1] * CS, CS, CS))
        if self.eda[3] < 20 and self.eda[3] % 2 == 0:
            pygame.draw.rect(screen, (0, 0, 0), (self.eda[0] * CS, self.eda[1] * CS, CS, CS))

        if self.poison:
            pygame.draw.rect(screen, (139, 0, 0), (self.poison[0] * CS, self.poison[1] * CS, CS, CS))

        if self.powerup:
            colors = {"speed": (0, 255, 255), "slow": (255, 165, 0), "shield": (255, 255, 0)}
            pygame.draw.circle(screen, colors[self.powerup[2]],
                               (self.powerup[0]*CS + CS//2, self.powerup[1]*CS + CS//2), CS//2)

        for obs in self.obstacles:
            pygame.draw.rect(screen, (100, 100, 100), (obs[0] * CS, obs[1] * CS, CS, CS))

        for s in self.zmeika:
            col = (255, 255, 0) if self.shield_active else self.settings["snake_color"]
            pygame.draw.rect(screen, col, (s[0] * CS, s[1] * CS, CS, CS))

        font = pygame.font.SysFont("Verdana", 16)
        txt_sc = font.render(f"Score: {self.sc} | PB: {self.pb}", True, (255, 255, 255))
        txt_lvl = font.render(f"Level: {self.lvl}", True, (255, 255, 255))
        screen.blit(txt_sc, (10, 10))
        screen.blit(txt_lvl, ((W * CS) - txt_lvl.get_width() - 10, 10))
