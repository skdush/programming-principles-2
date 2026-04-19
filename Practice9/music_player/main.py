import pygame
import sys
import os
from player import MusicPlayer

WIDTH, HEIGHT = 700, 420
FPS = 60

BG_COLOR = (20, 20, 35)
PANEL_COLOR = (35, 35, 55)
WHITE = (255, 255, 255)
GRAY = (160, 160, 180)
GREEN = (50, 220, 100)
RED = (220, 60, 60)
YELLOW = (255, 210, 0)
BLUE = (80, 140, 255)
DARK = (10, 10, 20)


def draw_progress_bar(screen, x, y, w, h, progress, bg, fg):
    pygame.draw.rect(screen, bg, (x, y, w, h), border_radius=4)
    if progress > 0:
        pygame.draw.rect(screen, fg, (x, y, int(w * progress), h), border_radius=4)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Music Player")
    clock = pygame.time.Clock()

    music_dir = os.path.join(os.path.dirname(__file__), "music")
    player = MusicPlayer(music_dir)

    font_big = pygame.font.SysFont("Arial", 30, bold=True)
    font_med = pygame.font.SysFont("Arial", 22)
    font_small = pygame.font.SysFont("Courier New", 16)
    font_key = pygame.font.SysFont("Courier New", 18, bold=True)

    elapsed_time = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                player.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                    elapsed_time = 0.0
                elif event.key == pygame.K_s:
                    player.stop()
                    elapsed_time = 0.0
                elif event.key == pygame.K_n:
                    player.next_track()
                    elapsed_time = 0.0
                elif event.key == pygame.K_b:
                    player.prev_track()
                    elapsed_time = 0.0
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    player.stop()
                    pygame.quit()
                    sys.exit()

        player.update()

        if player.is_playing:
            elapsed_time += dt

        screen.fill(BG_COLOR)

        title = font_big.render("Music Player", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        pygame.draw.rect(screen, PANEL_COLOR, (40, 70, WIDTH - 80, 120), border_radius=10)

        track_name = player.get_current_track_name()
        if len(track_name) > 45:
            track_name = track_name[:42] + "..."
        track_surf = font_med.render(track_name, True, WHITE)
        screen.blit(track_surf, (60, 85))

        count = player.get_track_count()
        idx_text = f"Track {player.current_index + 1} of {count}" if count else "No tracks"
        idx_surf = font_small.render(idx_text, True, GRAY)
        screen.blit(idx_surf, (60, 120))

        if player.is_playing:
            status_text = "► PLAYING"
            status_color = GREEN
        elif player.is_stopped:
            status_text = "■ STOPPED"
            status_color = RED
        else:
            status_text = "■ STOPPED"
            status_color = GRAY
        status_surf = font_med.render(status_text, True, status_color)
        screen.blit(status_surf, (WIDTH - 60 - status_surf.get_width(), 85))

        max_display = 180.0
        progress = min(elapsed_time / max_display, 1.0)
        draw_progress_bar(screen, 60, 155, WIDTH - 120, 14, progress, DARK, BLUE)

        mins = int(elapsed_time) // 60
        secs = int(elapsed_time) % 60
        time_str = f"{mins:02d}:{secs:02d}"
        time_surf = font_small.render(time_str, True, GRAY)
        screen.blit(time_surf, (60, 174))

        pygame.draw.rect(screen, PANEL_COLOR, (40, 210, WIDTH - 80, 170), border_radius=10)

        controls_title = font_med.render("Keyboard Controls:", True, YELLOW)
        screen.blit(controls_title, (60, 220))

        controls = [
            ("[P]", "Play current track"),
            ("[S]", "Stop"),
            ("[N]", "Next track"),
            ("[B]", "Previous track"),
            ("[Q] / [Esc]", "Quit"),
        ]
        for i, (key, desc) in enumerate(controls):
            key_surf = font_key.render(key, True, GREEN)
            desc_surf = font_small.render(desc, True, WHITE)
            screen.blit(key_surf, (60, 248 + i * 24))
            screen.blit(desc_surf, (180, 250 + i * 24))

        if count == 0:
            hint = font_small.render(
                "Put MP3/WAV/OGG files into the 'music/' folder", True, RED
            )
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()


if __name__ == "__main__":
    main()
