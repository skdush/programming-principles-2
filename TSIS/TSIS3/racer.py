import pygame, random
from persistence import load_settings

SCREEN_W, SCREEN_H = 400, 600

class Player(pygame.sprite.Sprite):
    def __init__(self, color_name):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        colors = {"blue": (0, 0, 255), "red": (255, 0, 0), "green": (0, 255, 0)}
        self.image.fill(colors.get(color_name, (0, 0, 255)))
        self.rect = self.image.get_rect(center=(160, 520))
        self.shield_active = False

    def move(self):
        k = pygame.key.get_pressed()
        if k[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)
        if k[pygame.K_RIGHT] and self.rect.right < SCREEN_W:
            self.rect.move_ip(5, 0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, existing_sprites):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill((200, 0, 0))
        self.rect = self.image.get_rect()
        self.safe_spawn(existing_sprites)

    def safe_spawn(self, existing_sprites):
        while True:
            self.rect.center = (random.randint(40, 360), random.randint(-200, -50))
            if not pygame.sprite.spritecollideany(self, existing_sprites):
                break

    def update(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_H:
            self.kill()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, existing_sprites):
        super().__init__()
        self.image = pygame.Surface((50, 20))
        self.image.fill((50, 50, 50))
        self.rect = self.image.get_rect()
        self.safe_spawn(existing_sprites)

    def safe_spawn(self, existing_sprites):
        while True:
            self.rect.center = (random.randint(40, 360), random.randint(-200, -50))
            if not pygame.sprite.spritecollideany(self, existing_sprites):
                break

    def update(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_H:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, existing_sprites):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.type = random.choice(["nitro", "shield", "repair"])
        colors = {"nitro": (0, 255, 255), "shield": (255, 255, 0), "repair": (0, 255, 0)}
        self.image.fill(colors[self.type])
        self.rect = self.image.get_rect()
        self.safe_spawn(existing_sprites)

    def safe_spawn(self, existing_sprites):
        while True:
            self.rect.center = (random.randint(40, 360), random.randint(-200, -50))
            if not pygame.sprite.spritecollideany(self, existing_sprites):
                break

    def update(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_H:
            self.kill()

def run_game(screen, clock):
    settings = load_settings()
    base_spd = 5 if settings["difficulty"] == "normal" else (3 if settings["difficulty"] == "easy" else 7)

    player = Player(settings["color"])
    all_sprites = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    score, distance, coins = 0, 0, 0
    active_power = None
    power_timer = 0

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "QUIT", score, distance

        enemy_spawn_chance = max(15, 60 - (distance // 100))
        obs_spawn_chance = max(30, 100 - (distance // 100))

        if random.randint(1, enemy_spawn_chance) == 1:
            enemy = Enemy(all_sprites)
            enemies.add(enemy)
            all_sprites.add(enemy)
        if random.randint(1, obs_spawn_chance) == 1:
            obs = Obstacle(all_sprites)
            obstacles.add(obs)
            all_sprites.add(obs)
        if random.randint(1, 300) == 1:
            pw = PowerUp(all_sprites)
            powerups.add(pw)
            all_sprites.add(pw)

        current_spd = base_spd + (distance // 1000)
        if active_power == "nitro":
            current_spd += 5
            power_timer -= 1
            if power_timer <= 0:
                active_power = None

        player.move()
        enemies.update(current_spd)
        obstacles.update(current_spd)
        powerups.update(current_spd)

        distance += current_spd // 2
        score = (distance // 10) + (coins * 10)

        hit_pw = pygame.sprite.spritecollideany(player, powerups)
        if hit_pw:
            active_power = hit_pw.type
            if active_power == "nitro": power_timer = 180
            elif active_power == "shield": player.shield_active = True
            elif active_power == "repair":
                for obs in obstacles: obs.kill()
            hit_pw.kill()

        hit_hazard = pygame.sprite.spritecollideany(player, enemies) or pygame.sprite.spritecollideany(player, obstacles)
        if hit_hazard:
            if player.shield_active:
                player.shield_active = False
                hit_hazard.kill()
            else:
                return "GAME_OVER", score, distance

        screen.fill((100, 100, 100))
        all_sprites.draw(screen)

        from ui import draw_text
        draw_text(screen, f"Score: {score} | Dist: {distance}", 10, 10, (255, 255, 255))
        if active_power:
            draw_text(screen, f"POWER: {active_power.upper()}", 10, 40, (0, 255, 255))
        if player.shield_active:
            pygame.draw.rect(screen, (255, 255, 0), player.rect, 2)

        draw_text(screen, f"Speed: {current_spd}", 10, 70, (255, 255, 255))

        pygame.display.update()
        clock.tick(60)
