import pygame, sys
from racer import run_game
from persistence import save_score, load_leaderboard
from ui import Button, draw_text, font_lg

pygame.init()
SCREEN_W, SCREEN_H = 400, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("TSIS 3 Racer")
clock = pygame.time.Clock()

def menu_screen():
    btn_play = Button(100, 200, 200, 50, "Play")
    btn_quit = Button(100, 340, 200, 50, "Quit")
    btn_leader = Button(100, 270, 200, 50, "Leaderboard")

    while True:
        screen.fill((255, 255, 255))
        draw_text(screen, "MAIN MENU", SCREEN_W//2, 100, font=font_lg, center=True)
        btn_play.draw(screen)
        btn_leader.draw(screen)
        btn_quit.draw(screen)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "QUIT"
            if btn_play.is_clicked(e): return "PLAY"
            if btn_leader.is_clicked(e): return "LEADERBOARD"
            if btn_quit.is_clicked(e): return "QUIT"

        pygame.display.update()
        clock.tick(60)

def game_over_screen(score, distance):
    btn_menu = Button(100, 350, 200, 50, "Main Menu")
    save_score("Player", score, distance)

    while True:
        screen.fill((200, 50, 50))
        draw_text(screen, "GAME OVER", SCREEN_W//2, 150, font=font_lg, center=True)
        draw_text(screen, f"Score: {score}", SCREEN_W//2, 220, center=True)
        draw_text(screen, f"Distance: {distance}", SCREEN_W//2, 260, center=True)
        btn_menu.draw(screen)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "QUIT"
            if btn_menu.is_clicked(e): return "MENU"

        pygame.display.update()
        clock.tick(60)

def leaderboard_screen():
    btn_back = Button(100, 500, 200, 50, "Back")
    board = load_leaderboard()

    while True:
        screen.fill((255, 255, 255))
        draw_text(screen, "TOP 10", SCREEN_W//2, 50, font=font_lg, center=True)

        y = 120
        for i, entry in enumerate(board):
            draw_text(screen, f"{i+1}. {entry['name']} - {entry['score']}", 50, y)
            y += 30

        btn_back.draw(screen)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "QUIT"
            if btn_back.is_clicked(e): return "MENU"

        pygame.display.update()
        clock.tick(60)

def main():
    state = "MENU"
    while True:
        if state == "MENU":
            state = menu_screen()
        elif state == "PLAY":
            result, score, distance = run_game(screen, clock)
            if result == "QUIT": break
            state = "GAME_OVER"
        elif state == "GAME_OVER":
            state = game_over_screen(score, distance)
        elif state == "LEADERBOARD":
            state = leaderboard_screen()
        elif state == "QUIT":
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
