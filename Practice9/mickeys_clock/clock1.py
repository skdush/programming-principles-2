import pygame
import math
import datetime

def draw_clock(screen, center, radius):
    now = datetime.datetime.now()
    minutes = now.minute
    seconds = now.second

    pygame.draw.circle(screen, (255, 255, 255), center, radius)
    pygame.draw.circle(screen, (0, 0, 0), center, radius, 4)

    import os
    hand = pygame.image.load(os.path.join(os.path.dirname(__file__), "images", "mickey_hand.png")).convert_alpha()

    def draw_hand(angle, length):
        scaled = pygame.transform.scale(hand, (40, int(length)))
        rotated = pygame.transform.rotate(scaled, -math.degrees(angle) - 90)
        ox = int(length / 2 * math.cos(angle))
        oy = int(length / 2 * math.sin(angle))
        rect = rotated.get_rect(center=(center[0] + ox, center[1] + oy))
        screen.blit(rotated, rect)

    min_angle = math.radians(minutes * 6 - 90)
    draw_hand(min_angle, radius * 0.7)

    sec_angle = math.radians(seconds * 6 - 90)
    draw_hand(sec_angle, radius * 0.9)