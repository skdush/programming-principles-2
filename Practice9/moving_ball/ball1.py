import pygame

class Ball:
    RADIUS = 25
    STEP = 20

    def __init__(self, screen_width, screen_height):
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.screen_width = screen_width
        self.screen_height = screen_height

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
        pygame.draw.circle(screen, (220, 50, 50), (self.x, self.y), self.RADIUS)