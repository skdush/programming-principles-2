import pygame
import sys
import json
import os

pygame.init()

from game import Game, WIDTH, HEIGHT, HUD_H, GAME_H, GAME_W

try:
    import db as _db
    _db.setup_db()
    DB_OK = True
except Exception:
    DB_OK = False

_DIR = os.path.dirname(os.path.abspath(__file__))
_SETTINGS_FILE = os.path.join(_DIR, "settings.json")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake — TSIS4")
clock  = pygame.time.Clock()

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (100, 100, 100)
DARK   = (25,  25,  25)
RED    = (220, 50,  50)
GREEN  = (50,  200, 50)
YELLOW = (255, 215, 0)
BLUE   = (80,  150, 255)
ORANGE = (255, 140, 0)
TEAL   = (0,   180, 160)


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _center(surface, text, y, size=24, color=WHITE, bold=False):
    lbl = _font(size, bold).render(text, True, color)
    surface.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, y))


def _btn(surface, text, rect, color=GRAY, fg=WHITE):
    pygame.draw.rect(surface, color, rect, border_radius=7)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=7)
    lbl = _font(20).render(text, True, fg)
    surface.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                        rect.centery - lbl.get_height() // 2))


def load_settings():
    if os.path.exists(_SETTINGS_FILE):
        with open(_SETTINGS_FILE) as f:
            return json.load(f)
    return {"snake_color": [50, 200, 50], "grid_overlay": True, "sound": False}


def save_settings_file(s):
    with open(_SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)


def main_menu(settings):
    name_rect   = pygame.Rect(80, 140, 240, 36)
    btn_play    = pygame.Rect(100, 200, 200, 46)
    btn_lb      = pygame.Rect(100, 260, 200, 46)
    btn_cfg     = pygame.Rect(100, 320, 200, 46)
    btn_quit    = pygame.Rect(100, 380, 200, 46)
    username    = ""
    inp_active  = True

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                inp_active = name_rect.collidepoint(mx, my)
                if btn_play.collidepoint(mx, my):
                    return "play", username.strip() or "Player"
                if btn_lb.collidepoint(mx, my):
                    return "leaderboard", username.strip() or "Player"
                if btn_cfg.collidepoint(mx, my):
                    return "settings", username.strip() or "Player"
                if btn_quit.collidepoint(mx, my):
                    pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and inp_active:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode and event.unicode.isprintable() and len(username) < 16:
                    username += event.unicode

        screen.fill(DARK)
        _center(screen, "SNAKE",  50, 52, YELLOW, bold=True)
        _center(screen, "TSIS4", 105, 22, ORANGE)
        _center(screen, "Your name:", 118, 18, GRAY)
        pygame.draw.rect(screen, (60, 60, 80) if inp_active else (40, 40, 55),
                         name_rect, border_radius=6)
        pygame.draw.rect(screen, YELLOW if inp_active else GRAY, name_rect, 2, border_radius=6)
        lbl = _font(20).render(username or "Enter name...", True,
                                WHITE if username else GRAY)
        screen.blit(lbl, (name_rect.x + 8, name_rect.y + 8))
        _btn(screen, "Play",        btn_play,  GREEN)
        _btn(screen, "Leaderboard", btn_lb,    BLUE)
        _btn(screen, "Settings",    btn_cfg,   GRAY)
        _btn(screen, "Quit",        btn_quit,  RED)
        pygame.display.flip()


def game_over_screen(score, level, personal_best):
    btn_retry = pygame.Rect(60,  370, 130, 46)
    btn_menu  = pygame.Rect(210, 370, 130, 46)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if btn_retry.collidepoint(mx, my):
                    return "retry"
                if btn_menu.collidepoint(mx, my):
                    return "menu"

        screen.fill(DARK)
        _center(screen, "GAME OVER",   90,  44, RED, bold=True)
        _center(screen, f"Score: {score}",      175, 28, WHITE)
        _center(screen, f"Level: {level}",      215, 28, WHITE)
        _center(screen, f"Personal best: {personal_best}", 255, 22, YELLOW)
        _btn(screen, "Retry",     btn_retry, GREEN)
        _btn(screen, "Main Menu", btn_menu,  GRAY)
        pygame.display.flip()


def leaderboard_screen():
    btn_back = pygame.Rect(130, 530, 140, 44)
    if DB_OK:
        try:
            rows = _db.get_top10()
        except Exception:
            rows = []
    else:
        rows = []

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(*event.pos):
                    return

        screen.fill(DARK)
        _center(screen, "LEADERBOARD", 18, 36, YELLOW, bold=True)
        hdr = _font(16).render(
            f"{'#':<3} {'Name':<12} {'Score':>6} {'Level':>5} {'Date':>12}", True, ORANGE)
        screen.blit(hdr, (20, 68))
        pygame.draw.line(screen, GRAY, (20, 90), (WIDTH - 20, 90), 1)
        for i, r in enumerate(rows[:10]):
            col = YELLOW if i == 0 else WHITE
            line = f"{i+1:<3} {r[0]:<12} {r[1]:>6} {r[2]:>5} {str(r[3]):>12}"
            screen.blit(_font(16).render(line, True, col), (20, 100 + i * 38))
        if not rows:
            _center(screen, "No records yet", 200, 22, GRAY)
        _btn(screen, "Back", btn_back, GRAY)
        pygame.display.flip()


def settings_screen(settings):
    btn_grid  = pygame.Rect(80, 160, 240, 44)
    btn_sound = pygame.Rect(80, 220, 240, 44)
    btn_red   = pygame.Rect(50,  310, 50, 50)
    btn_green = pygame.Rect(120, 310, 50, 50)
    btn_blue  = pygame.Rect(190, 310, 50, 50)
    btn_yel   = pygame.Rect(260, 310, 50, 50)
    btn_save  = pygame.Rect(80, 390, 240, 44)

    colors = [
        (btn_red,   [220, 50, 50]),
        (btn_green, [50, 200, 50]),
        (btn_blue,  [80, 150, 255]),
        (btn_yel,   [220, 200, 50]),
    ]
    cfg = dict(settings)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if btn_grid.collidepoint(mx, my):
                    cfg["grid_overlay"] = not cfg["grid_overlay"]
                if btn_sound.collidepoint(mx, my):
                    cfg["sound"] = not cfg["sound"]
                for r, col in colors:
                    if r.collidepoint(mx, my):
                        cfg["snake_color"] = col
                if btn_save.collidepoint(mx, my):
                    save_settings_file(cfg)
                    settings.update(cfg)
                    return

        screen.fill(DARK)
        _center(screen, "SETTINGS", 25, 36, YELLOW, bold=True)
        _center(screen, "Grid Overlay", 130, 20, WHITE)
        _btn(screen, "ON" if cfg["grid_overlay"] else "OFF", btn_grid,
             GREEN if cfg["grid_overlay"] else RED)
        _center(screen, "Sound", 193, 20, WHITE)
        _btn(screen, "ON" if cfg["sound"] else "OFF", btn_sound,
             GREEN if cfg["sound"] else RED)
        _center(screen, "Snake Color", 280, 20, WHITE)
        for r, col in colors:
            sel = (cfg["snake_color"] == col)
            pygame.draw.rect(screen, tuple(col), r, border_radius=6)
            pygame.draw.rect(screen, YELLOW if sel else WHITE, r, 3, border_radius=6)
        _btn(screen, "Save & Back", btn_save, BLUE)
        pygame.display.flip()


def run():
    settings = load_settings()
    username = "Player"

    while True:
        action, username = main_menu(settings)

        if action == "leaderboard":
            leaderboard_screen()
            continue
        if action == "settings":
            settings_screen(settings)
            continue

        pb = 0
        if DB_OK:
            try:
                pb = _db.get_personal_best(username)
            except Exception:
                pb = 0

        game = Game(username, settings, pb)

        while not game.game_over:
            dt = clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    game.handle_key(event.key)
            game.update(dt)
            game.draw(screen)
            pygame.display.flip()

        if DB_OK:
            try:
                _db.save_result(username, game.score, game.level)
                pb = _db.get_personal_best(username)
            except Exception:
                pass

        result = game_over_screen(game.score, game.level, pb)
        if result == "retry":
            game = Game(username, settings, pb)


if __name__ == "__main__":
    run()
