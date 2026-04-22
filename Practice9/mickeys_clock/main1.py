import pygame
import sys
from clock1 import draw_clock

WIDTH, HEIGHT = 600, 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey's Clock")
clock_tick = pygame.time.Clock()

center = (WIDTH // 2, HEIGHT // 2)
radius = 200

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((240, 240, 255))
    draw_clock(screen, center, radius)
    pygame.display.flip()
    clock_tick.tick(FPS)