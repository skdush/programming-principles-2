import pygame

# Цвета
RED = (220, 50, 50)
DARK_RED = (150, 20, 20)


class Ball:
    RADIUS = 25
    STEP = 4           # пикселей за кадр (зажатие)

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Начальное положение — центр экрана
        self.x = screen_width // 2
        self.y = screen_height // 2

    def move(self, direction):
        """
        Двигает мяч на STEP пикселей в нужную сторону.
        direction: "up", "down", "left", "right"
        Граница проверяется ПЕРЕД движением — если выйдем за экран, игнорируем.
        """
        new_x, new_y = self.x, self.y

        if direction == "up":
            new_y -= self.STEP
        elif direction == "down":
            new_y += self.STEP
        elif direction == "left":
            new_x -= self.STEP
        elif direction == "right":
            new_x += self.STEP

        # Проверка границ: мяч не должен выходить за пределы экрана
        if (self.RADIUS <= new_x <= self.screen_width - self.RADIUS and
                self.RADIUS <= new_y <= self.screen_height - self.RADIUS):
            self.x = new_x
            self.y = new_y
        # Если новая позиция за границей — движение игнорируется

    def draw(self, screen):
        """Рисует мяч с небольшой тенью для объёма"""
        # Тень
        pygame.draw.circle(screen, (180, 180, 180), (self.x + 4, self.y + 4), self.RADIUS)
        # Основной круг
        pygame.draw.circle(screen, RED, (self.x, self.y), self.RADIUS)
        # Контур
        pygame.draw.circle(screen, DARK_RED, (self.x, self.y), self.RADIUS, 3)
        # Блик (маленький белый кружок)
        pygame.draw.circle(screen, (255, 180, 180),
                           (self.x - self.RADIUS // 3, self.y - self.RADIUS // 3), 7)
