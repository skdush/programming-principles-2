import pygame

pygame.font.init()
font_sm = pygame.font.SysFont("Verdana", 20)
font_lg = pygame.font.SysFont("Verdana", 40)

def draw_text(surface, text, x, y, color=(0, 0, 0), font=font_sm, center=False):
    txt_surf = font.render(text, True, color)
    rect = txt_surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(txt_surf, rect)

class Button:
    def __init__(self, x, y, w, h, text, color=(200, 200, 200)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        draw_text(surface, self.text, self.rect.centerx, self.rect.centery, center=True)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False