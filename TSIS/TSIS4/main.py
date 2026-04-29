import pygame, sys
from config import WIDTH, HEIGHT, load_settings, save_settings
from db import save_session, get_top_10, get_personal_best
from game import SnakeGame

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 4 - Database Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 20)

def draw_text(text, x, y, center=True, color=(255,255,255)):
    txt = font.render(text, True, color)
    rect = txt.get_rect(center=(x,y)) if center else txt.get_rect(topleft=(x,y))
    screen.blit(txt, rect)

def draw_button(text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, (70, 70, 70), rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
    draw_text(text, x + w//2, y + h//2)
    return rect

def main_menu():
    username = ""
    input_active = False
    while True:
        screen.fill((20, 20, 20))
        draw_text("TSIS 4 SNAKE", WIDTH//2, 40, color=(0, 255, 0))

        draw_text("Username:", WIDTH//2, 90)
        input_rect = pygame.Rect(WIDTH//2 - 100, 110, 200, 35)
        pygame.draw.rect(screen, (50, 50, 50) if input_active else (30, 30, 30), input_rect)
        draw_text(username + ("|" if input_active else ""), WIDTH//2, 127)

        play_btn = draw_button("Play", WIDTH//2 - 100, 170, 200, 40)
        lead_btn = draw_button("Leaderboard", WIDTH//2 - 100, 230, 200, 40)
        set_btn = draw_button("Settings", WIDTH//2 - 100, 290, 200, 40)
        quit_btn = draw_button("Quit", WIDTH//2 - 100, 350, 200, 40)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                input_active = input_rect.collidepoint(e.pos)
                if play_btn.collidepoint(e.pos) and username.strip(): return "PLAY", username.strip()
                if lead_btn.collidepoint(e.pos): return "LEADERBOARD", username
                if set_btn.collidepoint(e.pos): return "SETTINGS", username
                if quit_btn.collidepoint(e.pos): sys.exit()
            if e.type == pygame.KEYDOWN and input_active:
                if e.key == pygame.K_BACKSPACE: username = username[:-1]
                elif len(username) < 15: username += e.unicode

        pygame.display.flip()

def leaderboard_screen():
    try:
        top_10 = get_top_10()
    except Exception as e:
        top_10 = []
        print("DB Error:", e)

    while True:
        screen.fill((20, 20, 20))
        draw_text("TOP 10 LEADERBOARD", WIDTH//2, 30)

        y = 70
        for i, row in enumerate(top_10):
            draw_text(f"{i+1}. {row[0]} - Sc: {row[1]} (Lv {row[2]})", WIDTH//2, y)
            y += 25

        back_btn = draw_button("Back", WIDTH//2 - 100, 340, 200, 40)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and back_btn.collidepoint(e.pos): return

        pygame.display.flip()

def settings_screen():
    settings = load_settings()
    colors = [(0, 255, 0), (0, 0, 255), (255, 0, 255)]
    c_idx = colors.index(settings["snake_color"]) if settings["snake_color"] in colors else 0

    while True:
        screen.fill((20, 20, 20))
        draw_text("SETTINGS", WIDTH//2, 50)

        grid_btn = draw_button(f"Grid: {'ON' if settings['grid_overlay'] else 'OFF'}", WIDTH//2 - 100, 120, 200, 40)
        col_btn = draw_button(f"Color: RGB{settings['snake_color']}", WIDTH//2 - 150, 190, 300, 40)
        back_btn = draw_button("Save & Back", WIDTH//2 - 100, 280, 200, 40)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if grid_btn.collidepoint(e.pos):
                    settings["grid_overlay"] = not settings["grid_overlay"]
                if col_btn.collidepoint(e.pos):
                    c_idx = (c_idx + 1) % len(colors)
                    settings["snake_color"] = colors[c_idx]
                if back_btn.collidepoint(e.pos):
                    save_settings(settings)
                    return

        pygame.display.flip()

def run_game_loop(username):
    try:
        pb = get_personal_best(username)
    except:
        pb = 0

    game = SnakeGame(username, pb)

    while not game.game_over:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and game.dy != 1: game.ndx, game.ndy = 0, -1
                elif e.key == pygame.K_DOWN and game.dy != -1: game.ndx, game.ndy = 0, 1
                elif e.key == pygame.K_LEFT and game.dx != 1: game.ndx, game.ndy = -1, 0
                elif e.key == pygame.K_RIGHT and game.dx != -1: game.ndx, game.ndy = 1, 0

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(game.get_speed())

    try:
        save_session(username, game.sc, game.lvl)
    except Exception as e:
        print("Could not save to DB:", e)

    while True:
        screen.fill((50, 0, 0))
        draw_text("GAME OVER", WIDTH//2, 100, color=(255, 0, 0))
        draw_text(f"Score: {game.sc} | Level: {game.lvl}", WIDTH//2, 160)

        retry_btn = draw_button("Retry", WIDTH//2 - 100, 230, 200, 40)
        menu_btn = draw_button("Main Menu", WIDTH//2 - 100, 300, 200, 40)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(e.pos): return "RETRY"
                if menu_btn.collidepoint(e.pos): return "MENU"
        pygame.display.flip()

def main():
    state = "MENU"
    username = ""
    while True:
        if state == "MENU":
            res, username = main_menu()
            state = res
        elif state == "LEADERBOARD":
            leaderboard_screen()
            state = "MENU"
        elif state == "SETTINGS":
            settings_screen()
            state = "MENU"
        elif state == "PLAY" or state == "RETRY":
            res = run_game_loop(username)
            state = "PLAY" if res == "RETRY" else "MENU"

if __name__ == "__main__":
    main()
