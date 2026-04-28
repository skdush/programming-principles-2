import pygame
import sys
from persistence import load_leaderboard, save_settings

WIDTH, HEIGHT = 400, 600

BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRAY   = (100, 100, 100)
DARK   = (30, 30, 30)
RED    = (220, 50, 50)
GREEN  = (50, 200, 50)
YELLOW = (255, 215, 0)
BLUE   = (50, 100, 220)
ORANGE = (255, 140, 0)

_font_cache = {}


def _font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont("Arial", size, bold=bold)
    return _font_cache[key]


def _btn(surface, text, rect, color=GRAY, text_color=WHITE, radius=8):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=radius)
    lbl = _font(20).render(text, True, text_color)
    surface.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                       rect.centery - lbl.get_height() // 2))


def _center_text(surface, text, y, size=28, color=WHITE, bold=False):
    lbl = _font(size, bold).render(text, True, color)
    surface.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, y))


def main_menu(surface, clock, username):
    btn_play  = pygame.Rect(100, 220, 200, 50)
    btn_lb    = pygame.Rect(100, 285, 200, 50)
    btn_cfg   = pygame.Rect(100, 350, 200, 50)
    btn_quit  = pygame.Rect(100, 415, 200, 50)
    name_rect = pygame.Rect(80, 160, 240, 36)

    input_active = False
    local_name   = username

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                input_active = name_rect.collidepoint(mx, my)
                if btn_play.collidepoint(mx, my):
                    return "play", local_name.strip() or "Player"
                if btn_lb.collidepoint(mx, my):
                    return "leaderboard", local_name.strip() or "Player"
                if btn_cfg.collidepoint(mx, my):
                    return "settings", local_name.strip() or "Player"
                if btn_quit.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    local_name = local_name[:-1]
                elif event.unicode and event.unicode.isprintable() and len(local_name) < 16:
                    local_name += event.unicode

        surface.fill(DARK)
        _center_text(surface, "RACER", 60, 52, YELLOW, bold=True)
        _center_text(surface, "TSIS3", 115, 22, ORANGE)

        pygame.draw.rect(surface, (60, 60, 80) if input_active else (40, 40, 55), name_rect, border_radius=6)
        pygame.draw.rect(surface, YELLOW if input_active else GRAY, name_rect, 2, border_radius=6)
        name_lbl = _font(20).render(local_name or "Enter name...", True,
                                     WHITE if local_name else GRAY)
        surface.blit(name_lbl, (name_rect.x + 8, name_rect.y + 8))

        _btn(surface, "Play",        btn_play,  GREEN)
        _btn(surface, "Leaderboard", btn_lb,    BLUE)
        _btn(surface, "Settings",    btn_cfg,   GRAY)
        _btn(surface, "Quit",        btn_quit,  RED)
        pygame.display.flip()


def game_over_screen(surface, clock, score, distance, coins):
    btn_retry = pygame.Rect(70,  390, 120, 50)
    btn_menu  = pygame.Rect(210, 390, 120, 50)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if btn_retry.collidepoint(mx, my):
                    return "retry"
                if btn_menu.collidepoint(mx, my):
                    return "menu"

        surface.fill(DARK)
        _center_text(surface, "GAME OVER", 90,  44, RED,    bold=True)
        _center_text(surface, f"Score:    {score}",    175, 26, WHITE)
        _center_text(surface, f"Distance: {distance} m", 215, 26, WHITE)
        _center_text(surface, f"Coins:    {coins}",    255, 26, YELLOW)
        _btn(surface, "Retry",     btn_retry, GREEN)
        _btn(surface, "Main Menu", btn_menu,  GRAY)
        pygame.display.flip()


def leaderboard_screen(surface, clock):
    btn_back = pygame.Rect(130, 530, 140, 46)
    entries  = load_leaderboard()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(*event.pos):
                    return

        surface.fill(DARK)
        _center_text(surface, "LEADERBOARD", 20, 36, YELLOW, bold=True)
        headers = f"{'#':<3} {'Name':<12} {'Score':>6} {'Dist':>6} {'Coins':>5}"
        surface.blit(_font(17).render(headers, True, ORANGE), (20, 75))
        pygame.draw.line(surface, GRAY, (20, 98), (WIDTH - 20, 98), 1)

        for i, e in enumerate(entries[:10]):
            color = YELLOW if i == 0 else WHITE
            line = (f"{i+1:<3} {e['username']:<12} "
                    f"{e['score']:>6} {e['distance']:>6} {e['coins']:>5}")
            surface.blit(_font(17).render(line, True, color), (20, 108 + i * 38))

        _btn(surface, "Back", btn_back, GRAY)
        pygame.display.flip()


def settings_screen(surface, clock, settings):
    btn_sound   = pygame.Rect(80, 170, 240, 46)
    btn_easy    = pygame.Rect(40, 290, 95,  46)
    btn_normal  = pygame.Rect(153, 290, 95, 46)
    btn_hard    = pygame.Rect(265, 290, 95, 46)
    btn_red     = pygame.Rect(55,  390, 50, 50)
    btn_blue    = pygame.Rect(120, 390, 50, 50)
    btn_green   = pygame.Rect(185, 390, 50, 50)
    btn_yellow  = pygame.Rect(250, 390, 50, 50)
    btn_save    = pygame.Rect(80,  490, 240, 46)

    color_opts = {
        "red":    [220, 50,  50],
        "blue":   [50,  100, 220],
        "green":  [50,  180, 50],
        "yellow": [220, 180, 50],
    }
    color_btns = [
        (btn_red,    color_opts["red"],    "R"),
        (btn_blue,   color_opts["blue"],   "B"),
        (btn_green,  color_opts["green"],  "G"),
        (btn_yellow, color_opts["yellow"], "Y"),
    ]

    cfg = dict(settings)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if btn_sound.collidepoint(mx, my):
                    cfg["sound"] = not cfg["sound"]
                if btn_easy.collidepoint(mx, my):
                    cfg["difficulty"] = "easy"
                if btn_normal.collidepoint(mx, my):
                    cfg["difficulty"] = "normal"
                if btn_hard.collidepoint(mx, my):
                    cfg["difficulty"] = "hard"
                for r, col, _ in color_btns:
                    if r.collidepoint(mx, my):
                        cfg["car_color"] = col
                if btn_save.collidepoint(mx, my):
                    save_settings(cfg)
                    settings.update(cfg)
                    return

        surface.fill(DARK)
        _center_text(surface, "SETTINGS", 30, 36, YELLOW, bold=True)

        _center_text(surface, "Sound", 130, 22, WHITE)
        sc = GREEN if cfg["sound"] else RED
        sl = "ON" if cfg["sound"] else "OFF"
        _btn(surface, f"Sound: {sl}", btn_sound, sc)

        _center_text(surface, "Difficulty", 255, 22, WHITE)
        for btn, diff in [(btn_easy, "easy"), (btn_normal, "normal"), (btn_hard, "hard")]:
            col = GREEN if cfg["difficulty"] == diff else GRAY
            _btn(surface, diff.capitalize(), btn, col, text_color=WHITE)

        _center_text(surface, "Car Color", 360, 22, WHITE)
        for r, col, label in color_btns:
            sel = (cfg["car_color"] == col)
            pygame.draw.rect(surface, tuple(col), r, border_radius=6)
            pygame.draw.rect(surface, YELLOW if sel else WHITE, r, 3, border_radius=6)

        _btn(surface, "Save & Back", btn_save, BLUE)
        pygame.display.flip()
