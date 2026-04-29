import pygame
import sys
import math
import datetime
from tools import flood_fill

pygame.init()

PANEL_W  = 185
CANVAS_W = 740
HEIGHT   = 640
WIDTH    = CANVAS_W + PANEL_W

WHITE    = (255, 255, 255)
BLACK    = (0, 0, 0)
GRAY     = (200, 200, 200)
DARK     = (60, 60, 60)
PANEL_BG = (225, 225, 225)
SEL_COL  = (80, 130, 220)

PALETTE = [
    BLACK, WHITE, (210, 30, 30),
    (30, 170, 30), (30, 30, 200), (255, 160, 0),
    (140, 0, 140), (0, 180, 180), (255, 20, 147),
    (139, 69, 19), (120, 120, 120), (255, 240, 0),
]

TOOLS     = ["Pencil", "Line", "Rect", "Circle",
             "R.Tri", "E.Tri", "Rhombus", "Eraser", "Fill", "Text"]
SIZES     = [2, 5, 10]
SIZE_LBLS = ["S(2)", "M(5)", "L(10)"]

screen   = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint — TSIS2")
clock    = pygame.time.Clock()
panel_f  = pygame.font.SysFont("Arial", 15)
canvas_f = pygame.font.SysFont("Arial", 20)

TOOL_H  = 28
TOOL_X  = CANVAS_W + 10
TOOL_W  = PANEL_W - 20

tool_rects = {
    t: pygame.Rect(TOOL_X, 30 + i * (TOOL_H + 4), TOOL_W, TOOL_H)
    for i, t in enumerate(TOOLS)
}
_sb = 30 + len(TOOLS) * (TOOL_H + 4) + 12
size_rects = [
    pygame.Rect(TOOL_X + i * (TOOL_W // 3 + 1), _sb, TOOL_W // 3, TOOL_H)
    for i in range(3)
]
_cb = _sb + TOOL_H + 14
color_rects = [
    pygame.Rect(TOOL_X + (i % 3) * 57, _cb + (i // 3) * 54, 50, 48)
    for i in range(len(PALETTE))
]


def draw_panel(tool, color_idx, size_idx):
    pygame.draw.rect(screen, PANEL_BG, (CANVAS_W, 0, PANEL_W, HEIGHT))
    pygame.draw.line(screen, DARK, (CANVAS_W, 0), (CANVAS_W, HEIGHT), 2)

    screen.blit(panel_f.render("Tools:", True, BLACK), (TOOL_X, 8))
    for t, r in tool_rects.items():
        bg = SEL_COL if t == tool else GRAY
        fg = WHITE if t == tool else BLACK
        pygame.draw.rect(screen, bg, r, border_radius=4)
        screen.blit(panel_f.render(t, True, fg), (r.x + 5, r.y + 6))

    screen.blit(panel_f.render("Brush:", True, BLACK), (TOOL_X, _sb - 14))
    for i, r in enumerate(size_rects):
        bg = SEL_COL if i == size_idx else GRAY
        fg = WHITE if i == size_idx else BLACK
        pygame.draw.rect(screen, bg, r, border_radius=4)
        screen.blit(panel_f.render(SIZE_LBLS[i], True, fg), (r.x + 3, r.y + 6))

    screen.blit(panel_f.render("Colors:", True, BLACK), (TOOL_X, _cb - 14))
    for i, r in enumerate(color_rects):
        pygame.draw.rect(screen, PALETTE[i], r)
        bw = 3 if i == color_idx else 1
        pygame.draw.rect(screen, BLACK, r, bw)

    hint = panel_f.render("Ctrl+S: save PNG", True, DARK)
    screen.blit(hint, (TOOL_X, HEIGHT - 20))


def draw_triangle_right(surface, color, s, e, lw):
    x1, y1 = s
    x2, y2 = e
    pygame.draw.polygon(surface, color, [(x1, y1), (x1, y2), (x2, y2)], lw)


def draw_triangle_equil(surface, color, s, e, lw):
    x1, y1 = s
    x2, y2 = e
    cx = (x1 + x2) / 2
    base = abs(x2 - x1)
    h = base * math.sqrt(3) / 2
    pygame.draw.polygon(surface, color,
                        [(cx, y1), (x1, y1 + h), (x2, y1 + h)], lw)


def draw_rhombus(surface, color, s, e, lw):
    x1, y1 = s
    x2, y2 = e
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    pygame.draw.polygon(surface, color,
                        [(cx, y1), (x2, cy), (cx, y2), (x1, cy)], lw)


def draw_shape(surface, tool, s, e, color, lw):
    x1, y1 = s
    x2, y2 = e
    if tool == "Rect":
        r = pygame.Rect(min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
        pygame.draw.rect(surface, color, r, lw)
    elif tool == "Circle":
        cx, cy = (x1+x2)//2, (y1+y2)//2
        rad = max(1, int(math.hypot(x2-x1, y2-y1)//2))
        pygame.draw.circle(surface, color, (cx, cy), rad, lw)
    elif tool == "Line":
        pygame.draw.line(surface, color, s, e, max(1, lw))
    elif tool == "R.Tri":
        draw_triangle_right(surface, color, s, e, lw)
    elif tool == "E.Tri":
        draw_triangle_equil(surface, color, s, e, lw)
    elif tool == "Rhombus":
        draw_rhombus(surface, color, s, e, lw)


def main():
    canvas = pygame.Surface((CANVAS_W, HEIGHT))
    canvas.fill(WHITE)

    tool      = "Pencil"
    color_idx = 0
    size_idx  = 1

    drawing  = False
    start    = None
    last_pos = None

    text_active = False
    text_pos    = None
    text_buf    = ""
    cursor_vis  = True
    cursor_t    = 0

    SHAPE_TOOLS = {"Rect", "Circle", "Line", "R.Tri", "E.Tri", "Rhombus"}

    running = True
    while running:
        clock.tick(60)
        cursor_t += 1
        if cursor_t >= 30:
            cursor_vis = not cursor_vis
            cursor_t   = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if event.key == pygame.K_1 and not text_active:
                    size_idx = 0
                elif event.key == pygame.K_2 and not text_active:
                    size_idx = 1
                elif event.key == pygame.K_3 and not text_active:
                    size_idx = 2
                if mods & pygame.KMOD_CTRL and event.key == pygame.K_s:
                    ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = f"canvas_{ts}.png"
                    pygame.image.save(canvas, fname)
                    print(f"Saved: {fname}")
                    continue

                if text_active:
                    if event.key == pygame.K_RETURN:
                        if text_buf and text_pos:
                            surf = canvas_f.render(text_buf, True, PALETTE[color_idx])
                            canvas.blit(surf, text_pos)
                        text_active = False
                        text_buf    = ""
                        text_pos    = None
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buf    = ""
                        text_pos    = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_buf = text_buf[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        text_buf += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if mx >= CANVAS_W:
                    for t, r in tool_rects.items():
                        if r.collidepoint(mx, my):
                            tool = t
                    for i, r in enumerate(size_rects):
                        if r.collidepoint(mx, my):
                            size_idx = i
                    for i, r in enumerate(color_rects):
                        if r.collidepoint(mx, my):
                            color_idx = i
                else:
                    if tool == "Fill":
                        flood_fill(canvas, mx, my, PALETTE[color_idx])
                    elif tool == "Text":
                        if text_active and text_buf and text_pos:
                            surf = canvas_f.render(text_buf, True, PALETTE[color_idx])
                            canvas.blit(surf, text_pos)
                        text_active = True
                        text_pos    = (mx, my)
                        text_buf    = ""
                    else:
                        drawing  = True
                        start    = (mx, my)
                        last_pos = (mx, my)
                        if tool == "Pencil":
                            pygame.draw.circle(canvas, PALETTE[color_idx],
                                               (mx, my), SIZES[size_idx])
                        elif tool == "Eraser":
                            pygame.draw.circle(canvas, WHITE,
                                               (mx, my), SIZES[size_idx] * 4)

            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                if mx < CANVAS_W:
                    if tool == "Pencil":
                        if last_pos:
                            pygame.draw.line(canvas, PALETTE[color_idx],
                                             last_pos, (mx, my), SIZES[size_idx] * 2)
                        pygame.draw.circle(canvas, PALETTE[color_idx],
                                           (mx, my), SIZES[size_idx])
                    elif tool == "Eraser":
                        if last_pos:
                            pygame.draw.line(canvas, WHITE,
                                             last_pos, (mx, my), SIZES[size_idx] * 8)
                        pygame.draw.circle(canvas, WHITE,
                                           (mx, my), SIZES[size_idx] * 4)
                    last_pos = (mx, my)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
                mx, my = pygame.mouse.get_pos()
                if tool in SHAPE_TOOLS and start:
                    ep = (min(mx, CANVAS_W - 1), my)
                    draw_shape(canvas, tool, start, ep,
                               PALETTE[color_idx], SIZES[size_idx])
                drawing  = False
                start    = None
                last_pos = None

        display = canvas.copy()

        if drawing and start and tool in SHAPE_TOOLS:
            mx, my = pygame.mouse.get_pos()
            ep     = (min(mx, CANVAS_W - 1), my)
            prev   = pygame.Surface((CANVAS_W, HEIGHT), pygame.SRCALPHA)
            pc     = (*PALETTE[color_idx], 140)
            draw_shape(prev, tool, start, ep, pc, SIZES[size_idx])
            display.blit(prev, (0, 0))

        if text_active and text_pos:
            txt = text_buf + ("|" if cursor_vis else " ")
            surf = canvas_f.render(txt, True, PALETTE[color_idx])
            display.blit(surf, text_pos)

        screen.blit(display, (0, 0))
        draw_panel(tool, color_idx, size_idx)
        pygame.display.flip()


if __name__ == "__main__":
    main()
