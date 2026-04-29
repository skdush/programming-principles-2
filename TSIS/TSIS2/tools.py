import pygame
from collections import deque

def flood_fill(surface, start_pos, fill_color):
    target_color = surface.get_at(start_pos)
    if target_color == fill_color:
        return

    width = surface.get_width()
    height = surface.get_height()

    queue = deque([start_pos])
    surface.set_at(start_pos, fill_color)

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while queue:
        x, y = queue.popleft()

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < width and 0 <= ny < height:
                if surface.get_at((nx, ny)) == target_color:
                    surface.set_at((nx, ny), fill_color)
                    queue.append((nx, ny))

def draw_shape(surface, shape_type, color, start_x, start_y, end_x, end_y, thickness):
    if shape_type == "line":
        pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), thickness)

    elif shape_type == "rect":
        rect = pygame.Rect(start_x, start_y, end_x - start_x, end_y - start_y)
        rect.normalize()
        pygame.draw.rect(surface, color, rect, thickness)

    elif shape_type == "circle":
        radius = int(((end_x - start_x)**2 + (end_y - start_y)**2)**0.5)
        pygame.draw.circle(surface, color, (start_x, start_y), radius, thickness)

    elif shape_type == "square":
        side = max(abs(end_x - start_x), abs(end_y - start_y))
        sign_x = 1 if end_x > start_x else -1
        sign_y = 1 if end_y > start_y else -1

        rect = pygame.Rect(start_x, start_y, side * sign_x, side * sign_y)
        rect.normalize()
        pygame.draw.rect(surface, color, rect, thickness)

    elif shape_type == "r_tri":
        points = [(start_x, start_y), (start_x, end_y), (end_x, end_y)]
        pygame.draw.polygon(surface, color, points, thickness)

    elif shape_type == "eq_tri":
        mid_x = start_x + (end_x - start_x) // 2
        points = [(mid_x, start_y), (start_x, end_y), (end_x, end_y)]
        pygame.draw.polygon(surface, color, points, thickness)

    elif shape_type == "rhomb":
        mid_x = start_x + (end_x - start_x) // 2
        mid_y = start_y + (end_y - start_y) // 2
        points = [(mid_x, start_y), (end_x, mid_y), (mid_x, end_y), (start_x, mid_y)]
        pygame.draw.polygon(surface, color, points, thickness)
