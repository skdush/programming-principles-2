import pygame
import sys
import datetime
from tools import draw_shape, flood_fill

pygame.init()


WIDTH, HEIGHT = 800, 600
UI_HEIGHT = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 2 Paint")
clock = pygame.time.Clock()

ui_font = pygame.font.SysFont("Verdana", 14)
text_tool_font = pygame.font.SysFont("Arial", 32)


canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))


current_color = (0, 0, 0)
current_tool = "brush"
brush_size = 5

is_drawing_shape = False
start_x, start_y = 0, 0
last_x, last_y = 0, 0

is_typing = False
text_input = ""
text_pos = (0, 0)


COLORS_UI = [
    (pygame.Rect(10, 10, 30, 30), (0, 0, 0)),
    (pygame.Rect(50, 10, 30, 30), (255, 0, 0)),
    (pygame.Rect(90, 10, 30, 30), (0, 255, 0)),
    (pygame.Rect(130, 10, 30, 30), (0, 0, 255))
]

TOOLS_UI = [
    (pygame.Rect(200, 10, 60, 25), "brush"),
    (pygame.Rect(270, 10, 60, 25), "eraser"),
    (pygame.Rect(340, 10, 60, 25), "rect"),
    (pygame.Rect(410, 10, 60, 25), "circle"),
    (pygame.Rect(480, 10, 60, 25), "line"),
    (pygame.Rect(550, 10, 60, 25), "text"),

    (pygame.Rect(200, 40, 60, 25), "square"),
    (pygame.Rect(270, 40, 60, 25), "r_tri"),
    (pygame.Rect(340, 40, 60, 25), "eq_tri"),
    (pygame.Rect(410, 40, 60, 25), "rhomb"),
    (pygame.Rect(480, 40, 60, 25), "fill")
]

def render_ui():
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, WIDTH, UI_HEIGHT))

    for rect, color in COLORS_UI:
        pygame.draw.rect(screen, color, rect)
        if color == current_color and current_tool != "eraser":
            pygame.draw.rect(screen, (255, 255, 255), rect, 3)

    for rect, tool_name in TOOLS_UI:
        bg_color = (150, 150, 150) if tool_name == current_tool else (100, 100, 100)
        pygame.draw.rect(screen, bg_color, rect)

        txt_surface = ui_font.render(tool_name, True, (255, 255, 255))
        screen.blit(txt_surface, txt_surface.get_rect(center=rect.center))

    info_txt = ui_font.render(f"Size (1,2,3): {brush_size} | Save: Ctrl+S", True, (50, 50, 50))
    screen.blit(info_txt, (10, 50))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if is_typing:
                if event.key == pygame.K_RETURN:
                    txt_surface = text_tool_font.render(text_input, True, current_color)
                    canvas.blit(txt_surface, text_pos)
                    is_typing = False
                    text_input = ""
                elif event.key == pygame.K_ESCAPE:
                    is_typing = False
                    text_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    text_input += event.unicode
            else:
                if event.key == pygame.K_1: brush_size = 2
                elif event.key == pygame.K_2: brush_size = 5
                elif event.key == pygame.K_3: brush_size = 10

                elif event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = f"canvas_{now}.png"
                    pygame.image.save(canvas, filename)
                    print(f"Saved: {filename}")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if event.pos[1] < UI_HEIGHT:
                    for rect, color in COLORS_UI:
                        if rect.collidepoint(event.pos):
                            current_color = color
                            if current_tool == "eraser":
                                current_tool = "brush"

                    for rect, tool_name in TOOLS_UI:
                        if rect.collidepoint(event.pos):
                            current_tool = tool_name
                else:
                    if current_tool == "fill":
                        flood_fill(canvas, event.pos, current_color)
                    elif current_tool == "text":
                        is_typing = True
                        text_input = ""
                        text_pos = event.pos
                    else:
                        is_drawing_shape = True
                        start_x, start_y = event.pos
                        last_x, last_y = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and is_drawing_shape:
                is_drawing_shape = False
                if current_tool not in ["brush", "eraser"]:
                    draw_shape(canvas, current_tool, current_color, start_x, start_y, event.pos[0], event.pos[1], brush_size)

        elif event.type == pygame.MOUSEMOTION:
            if is_drawing_shape:
                if current_tool == "brush":
                    pygame.draw.line(canvas, current_color, (last_x, last_y), event.pos, brush_size)
                    last_x, last_y = event.pos
                elif current_tool == "eraser":
                    pygame.draw.line(canvas, (255, 255, 255), (last_x, last_y), event.pos, brush_size * 4)
                    last_x, last_y = event.pos

    screen.blit(canvas, (0, 0))

    if is_drawing_shape and current_tool not in ["brush", "eraser"]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        draw_shape(screen, current_tool, current_color, start_x, start_y, mouse_x, mouse_y, brush_size)

    if is_typing:
        txt_surface = text_tool_font.render(text_input + "|", True, current_color)
        screen.blit(txt_surface, text_pos)

    render_ui()

    pygame.display.update()
    clock.tick(120)
