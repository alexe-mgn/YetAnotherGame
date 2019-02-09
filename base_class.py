import pygame
import random

class Level:

    def __init__(self, size=None):
        self.size = size if size is not None else [4000, 7200]
        self.surface = pygame.Surface(self.size)
        self.sprite_group = pygame.sprite.Group()
        for i in range(50):
            sprite = pygame.sprite.Sprite(self.sprite_group)
            sprite.image = pygame.Surface((20, 20))
            sprite.rect = sprite.image.get_rect()

            sprite.rect.topleft = [random.randrange(500), random.randrange(500)]
            pygame.draw.circle(sprite.image, (0, 200, 107), (10, 10), 10)

            #self.circle2 = pygame.draw.circle(self.surface, (0,200, 107), (200, 100), 30)


    def update(self):
        self.render()

    def render(self):
        self.sprite_group.draw(self.surface)

    def get_image(self, size=None, rect=pygame.Rect(0, 0, 102.4, 72)):
        if size is None:
            size = self.size[:]
        return pygame.transform.scale(self.surface.subsurface(rect), size)

if __name__ == '__main__':
    level = Level()
    screen = pygame.display.set_mode((1024, 720))
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
        screen.blit(level.get_image((1024, 720)), (0, 0))
        pygame.display.flip()
