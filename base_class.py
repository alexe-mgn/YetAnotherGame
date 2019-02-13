import pygame
import random


class Level:

    def __init__(self, size=None):
        self.size = size if size is not None else [600, 600]
        self.surface = pygame.Surface(self.size)
        self.screen = pygame.Rect(0, 0, *self.size)
        self.sprite_group = pygame.sprite.Group()
        for i in range(50):
            sprite = pygame.sprite.Sprite(self.sprite_group)
            sprite.image = pygame.Surface((20, 20)).convert_alpha()
            sprite.image.fill((255, 255, 255, 0))
            sprite.rect = sprite.image.get_rect()

            sprite.rect.topleft = [random.randrange(500), random.randrange(500)]
            pygame.draw.circle(sprite.image,
                               (random.randint(0, 255),
                                random.randint(0, 255),
                                random.randint(0, 255)),
                               (10, 10), 10)

            # self.circle2 = pygame.draw.circle(self.surface, (0,200, 107), (200, 100), 30)

    def update(self):
        self.render()

    def render(self):
        self.sprite_group.draw(self.surface)

    def get_screen(self, size):
        return pygame.transform.scale(self.get_image((0, 0, 400, 400)), size)

    def get_image(self, rect=None):
        if rect is None:
            rect = self.screen
        return self.surface.subsurface(rect)


if __name__ == '__main__':
    pygame.init()
    size = [1024, 720]
    screen = pygame.display.set_mode(size)
    level = Level()
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    pass
        screen.fill((0, 0, 0))
        level.render()
        screen.blit(level.get_screen(size), (0, 0))
        pygame.display.flip()
