import pygame

RED = (220, 50, 50)
DARK_RED = (150, 20, 20)


class Ball:
    RADIUS = 25
    STEP = 4

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width // 2
        self.y = screen_height // 2

    def move(self, direction):
        new_x, new_y = self.x, self.y

        if direction == "up":
            new_y -= self.STEP
        elif direction == "down":
            new_y += self.STEP
        elif direction == "left":
            new_x -= self.STEP
        elif direction == "right":
            new_x += self.STEP

        if (self.RADIUS <= new_x <= self.screen_width - self.RADIUS and
                self.RADIUS <= new_y <= self.screen_height - self.RADIUS):
            self.x = new_x
            self.y = new_y

    def draw(self, screen):
        pygame.draw.circle(screen, (180, 180, 180), (self.x + 4, self.y + 4), self.RADIUS)
        pygame.draw.circle(screen, RED, (self.x, self.y), self.RADIUS)
        pygame.draw.circle(screen, DARK_RED, (self.x, self.y), self.RADIUS, 3)
        pygame.draw.circle(screen, (255, 180, 180),
                           (self.x - self.RADIUS // 3, self.y - self.RADIUS // 3), 7)
