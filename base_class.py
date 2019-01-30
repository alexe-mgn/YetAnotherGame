import pygame


class Level:

    def __init__(self, size=None):
        self.size = size if size is not None else [1024, 720]
        self.surface = pygame.Surface(self.size)
        self.sprite_group = pygame.sprite.Group()
        sprite1 = pygame.sprite.Sprite(self.sprite_group)
        sprite1.image = pygame.Surface((50, 50))
        sprite1.rect = sprite1.image.get_rect()
        sprite1.rect.topleft = [200, 200]
        pygame.draw.circle(sprite1.image, (0,200, 107), (25,2), 25)

        #self.circle2 = pygame.draw.circle(self.surface, (0,200, 107), (200, 100), 30)


    def update(self):
        self.render()

    def render(self):
        self.sprite_group.draw(self.surface)

    def get_image(self):
        return self.surface


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
                    level.surface = pygame.transform.scale(level.surface, [int(e * 2) for e in level.surface.get_rect().size])
        screen.fill((0, 0, 0))
        level.render()
        screen.blit(level.get_image(), (0, 0))
        pygame.display.flip()
