import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 700, 560
TOOLBAR_H = 60
CANVAS_H = HEIGHT - TOOLBAR_H

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)
big_font = pygame.font.SysFont(None, 28)

PALETTE = [
    (0, 0, 0), (255, 255, 255), (200, 50, 50), (50, 150, 220),
    (50, 180, 50), (220, 180, 50), (180, 80, 200), (230, 120, 40),
    (100, 100, 100), (180, 180, 180),
]

MODES = ["Pencil", "Square", "Right Triangle", "Equilateral Triangle", "Rhombus", "Eraser"]
MODE_KEYS = {
    pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
    pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
}

BG_COLOR = (245, 245, 240)
TOOLBAR_COLOR = (50, 50, 60)
SELECTED_COLOR = (255, 200, 0)
CANVAS_BG = (255, 255, 255)


def draw_right_triangle(surface, color, start, end, width=2):
    """Draw right triangle: right angle at bottom-left."""
    x1, y1 = start
    x2, y2 = end
    p1 = (x1, y1)
    p2 = (x1, y2)
    p3 = (x2, y2)
    pygame.draw.polygon(surface, color, [p1, p2, p3], width)


def draw_equilateral_triangle(surface, color, start, end, width=2):
    """Draw equilateral triangle inscribed in bounding box."""
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) / 2
    base = abs(x2 - x1)
    h = base * math.sqrt(3) / 2
    p1 = (cx, y1)
    p2 = (x1, y1 + h)
    p3 = (x2, y1 + h)
    pygame.draw.polygon(surface, color, [p1, p2, p3], width)


def draw_rhombus(surface, color, start, end, width=2):
    """Draw rhombus (diamond shape) in bounding box."""
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    p1 = (cx, y1)
    p2 = (x2, cy)
    p3 = (cx, y2)
    p4 = (x1, cy)
    pygame.draw.polygon(surface, color, [p1, p2, p3, p4], width)


def draw_toolbar(surface, mode_idx, color, palette_rects, mode_rects, fill_mode):
    pygame.draw.rect(surface, TOOLBAR_COLOR, (0, 0, WIDTH, TOOLBAR_H))

    for i, (rect, name) in enumerate(zip(mode_rects, MODES)):
        is_selected = (i == mode_idx)
        btn_color = SELECTED_COLOR if is_selected else (80, 80, 90)
        pygame.draw.rect(surface, btn_color, rect, border_radius=4)
        pygame.draw.rect(surface, (150, 150, 160), rect, 1, border_radius=4)
        label = font.render(f"{i+1}:{name[:4]}", True, BLACK if is_selected else (200, 200, 200))
        surface.blit(label, (rect.x + 4, rect.y + 6))

    for i, (rect, col) in enumerate(zip(palette_rects, PALETTE)):
        pygame.draw.rect(surface, col, rect)
        if col == color:
            pygame.draw.rect(surface, SELECTED_COLOR, rect, 3)
        else:
            pygame.draw.rect(surface, (150, 150, 150), rect, 1)

    fill_rect = pygame.Rect(WIDTH - 80, 10, 70, 40)
    fill_col = (80, 200, 80) if fill_mode else (80, 80, 90)
    pygame.draw.rect(surface, fill_col, fill_rect, border_radius=4)
    label = font.render("Fill" if fill_mode else "Outline", True, WHITE)
    surface.blit(label, (fill_rect.x + 5, fill_rect.y + 12))

    swatch_rect = pygame.Rect(WIDTH - 160, 15, 30, 30)
    pygame.draw.rect(surface, color, swatch_rect)
    pygame.draw.rect(surface, WHITE, swatch_rect, 2)


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def main():
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill(CANVAS_BG)

    current_color = BLACK
    current_mode = 0
    fill_mode = False

    drawing = False
    start_pos = None
    pencil_points = []

    btn_w = 72
    btn_h = 40
    mode_rects = [
        pygame.Rect(4 + i * (btn_w + 3), 10, btn_w, btn_h)
        for i in range(len(MODES))
    ]

    pal_x_start = WIDTH - 160 - 10
    palette_rects = [
        pygame.Rect(pal_x_start - (len(PALETTE) - i) * 22, 18, 18, 24)
        for i in range(len(PALETTE))
    ]

    preview = pygame.Surface((WIDTH, CANVAS_H), pygame.SRCALPHA)

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in MODE_KEYS:
                    current_mode = MODE_KEYS[event.key]
                if event.key == pygame.K_f:
                    fill_mode = not fill_mode
                if event.key == pygame.K_c:
                    canvas.fill(CANVAS_BG)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if my < TOOLBAR_H:
                    for i, rect in enumerate(mode_rects):
                        if rect.collidepoint(mx, my):
                            current_mode = i
                    for i, (rect, col) in enumerate(zip(palette_rects, PALETTE)):
                        if rect.collidepoint(mx, my):
                            current_color = col
                    fill_rect = pygame.Rect(WIDTH - 80, 10, 70, 40)
                    if fill_rect.collidepoint(mx, my):
                        fill_mode = not fill_mode
                else:
                    drawing = True
                    start_pos = (mx, my - TOOLBAR_H)
                    pencil_points = [start_pos]

            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                if my >= TOOLBAR_H:
                    canvas_pos = (mx, my - TOOLBAR_H)
                    if current_mode == 0:  # Pencil
                        if pencil_points:
                            pygame.draw.line(canvas, current_color, pencil_points[-1], canvas_pos, 3)
                        pencil_points.append(canvas_pos)
                    elif current_mode == 5:  # Eraser
                        pygame.draw.circle(canvas, CANVAS_BG, canvas_pos, 15)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
                drawing = False
                mx, my = event.pos
                canvas_pos = (mx, my - TOOLBAR_H)
                thickness = 0 if fill_mode else 2  # 0 = filled polygon

                if start_pos and current_mode not in (0, 5):
                    if current_mode == 1:  # Square
                        x1, y1 = start_pos
                        x2, y2 = canvas_pos
                        w = x2 - x1
                        h = y2 - y1
                        pygame.draw.rect(canvas, current_color, (x1, y1, w, h), thickness)

                    elif current_mode == 2:  # Right Triangle
                        draw_right_triangle(canvas, current_color, start_pos, canvas_pos, thickness)

                    elif current_mode == 3:  # Equilateral Triangle
                        draw_equilateral_triangle(canvas, current_color, start_pos, canvas_pos, thickness)

                    elif current_mode == 4:  # Rhombus
                        draw_rhombus(canvas, current_color, start_pos, canvas_pos, thickness)

                start_pos = None
                pencil_points = []

        preview.fill((0, 0, 0, 0))
        if drawing and start_pos and current_mode not in (0, 5):
            mx, my = pygame.mouse.get_pos()
            canvas_pos = (mx, my - TOOLBAR_H)
            thickness = 0 if fill_mode else 2
            preview_color = (*current_color, 120)  # semi-transparent

            if current_mode == 1:
                x1, y1 = start_pos
                w, h = canvas_pos[0] - x1, canvas_pos[1] - y1
                pygame.draw.rect(preview, preview_color, (x1, y1, w, h), thickness)
            elif current_mode == 2:
                draw_right_triangle(preview, preview_color, start_pos, canvas_pos, thickness)
            elif current_mode == 3:
                draw_equilateral_triangle(preview, preview_color, start_pos, canvas_pos, thickness)
            elif current_mode == 4:
                draw_rhombus(preview, preview_color, start_pos, canvas_pos, thickness)

        screen.fill(TOOLBAR_COLOR)
        draw_toolbar(screen, current_mode, current_color, palette_rects, mode_rects, fill_mode)
        screen.blit(canvas, (0, TOOLBAR_H))
        screen.blit(preview, (0, TOOLBAR_H))

        help_text = font.render("1-6: tools  F: fill/outline  C: clear canvas", True, (180, 180, 180))
        screen.blit(help_text, (5, HEIGHT - 18))

        pygame.display.flip()


if __name__ == "__main__":
    main()