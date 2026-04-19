import pygame
import math
import datetime
import os

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (220, 50, 50)
YELLOW = (255, 230, 0)


class MickeysClock:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)
        self.radius = min(width, height) // 3

        self.hand_image = None
        hand_path = os.path.join(os.path.dirname(__file__), "images", "mickey_hand.png")
        if os.path.exists(hand_path):
            self.hand_image = pygame.image.load(hand_path).convert_alpha()

    def draw_clock_face(self):
        pygame.draw.circle(self.screen, WHITE, self.center, self.radius)
        pygame.draw.circle(self.screen, BLACK, self.center, self.radius, 4)

        for i in range(60):
            angle = math.radians(i * 6 - 90)
            if i % 5 == 0:
                inner = self.radius - 20
                outer = self.radius - 5
                width = 3
            else:
                inner = self.radius - 10
                outer = self.radius - 5
                width = 1
            x1 = self.center[0] + inner * math.cos(angle)
            y1 = self.center[1] + inner * math.sin(angle)
            x2 = self.center[0] + outer * math.cos(angle)
            y2 = self.center[1] + outer * math.sin(angle)
            pygame.draw.line(self.screen, BLACK, (x1, y1), (x2, y2), width)

        font = pygame.font.SysFont("Arial", 28, bold=True)
        positions = {
            12: (0, -(self.radius - 40)),
            3:  (self.radius - 40, 0),
            6:  (0, self.radius - 40),
            9:  (-(self.radius - 40), 0),
        }
        for num, (dx, dy) in positions.items():
            text = font.render(str(num), True, BLACK)
            rect = text.get_rect(center=(self.center[0] + dx, self.center[1] + dy))
            self.screen.blit(text, rect)

    def _get_angle(self, value, max_value):
        return math.radians(value / max_value * 360 - 90)

    def _draw_hand_with_image(self, image, angle, length):
        scale = length / max(image.get_width(), image.get_height())
        new_w = int(image.get_width() * scale)
        new_h = int(image.get_height() * scale)
        scaled = pygame.transform.scale(image, (new_w, new_h))

        degrees = -math.degrees(angle) - 90
        rotated = pygame.transform.rotate(scaled, degrees)

        offset_x = int(length / 2 * math.cos(angle))
        offset_y = int(length / 2 * math.sin(angle))
        rect = rotated.get_rect(center=(self.center[0] + offset_x,
                                        self.center[1] + offset_y))
        self.screen.blit(rotated, rect)

    def _draw_hand_line(self, angle, length, color, width):
        end_x = self.center[0] + int(length * math.cos(angle))
        end_y = self.center[1] + int(length * math.sin(angle))
        pygame.draw.line(self.screen, DARK_GRAY,
                         (self.center[0] + 2, self.center[1] + 2),
                         (end_x + 2, end_y + 2), width + 2)
        pygame.draw.line(self.screen, color, self.center, (end_x, end_y), width)

    def draw(self):
        now = datetime.datetime.now()
        minutes = now.minute
        seconds = now.second

        self.draw_clock_face()

        min_angle = self._get_angle(minutes + seconds / 60, 60)
        sec_angle = self._get_angle(seconds, 60)

        min_length = self.radius * 0.75
        sec_length = self.radius * 0.85

        if self.hand_image:
            self._draw_hand_with_image(self.hand_image, min_angle, min_length)
            self._draw_hand_with_image(self.hand_image, sec_angle, sec_length)
        else:
            self._draw_hand_line(min_angle, min_length, BLACK, 6)
            self._draw_hand_line(sec_angle, sec_length, RED, 3)

        pygame.draw.circle(self.screen, BLACK, self.center, 10)
        pygame.draw.circle(self.screen, YELLOW, self.center, 7)

        font = pygame.font.SysFont("Courier New", 32, bold=True)
        time_str = now.strftime("%M:%S")
        text = font.render(time_str, True, BLACK)
        rect = text.get_rect(center=(self.center[0], self.center[1] + self.radius + 30))
        self.screen.blit(text, rect)
