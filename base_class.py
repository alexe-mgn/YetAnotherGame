import pygame
import random
from geometry import FRect


class Camera:

    def __init__(self, center, size, constraint, min_size):
        self.constraint = constraint
        self.min_size = min_size
        self.rect = FRect(0, 0, *size)
        self.rect.center = center

    def get_rect(self):
        return self.rect.pygame

    def move(self, shift):
        if self.rect.right + shift[0] > self.constraint.right:
            shift[0] = 0
        if self.rect.left + shift[0] < 0:
            shift[0] = 0
        if self.rect.bottom + shift[1] > self.constraint.bottom:
            shift[1] = 0
        if self.rect.top + shift[1] < 0:
            shift[1] = 0
        self.rect.x += shift[0]
        self.rect.y += shift[1]

    def zoom(self, coef):
        center = self.rect.center
        premade = [self.rect.width / coef, self.rect.height / coef]
        if premade[0] < self.min_size[0] or premade[1] < self.min_size[1]:
            self.rect.size = self.min_size
        if premade[0] > self.constraint.size[0] or premade[1] > self.constraint.size[1]:
            self.rect.size = self.constraint
        self.rect.size = premade
        self.rect.center = center


class Level:

    def __init__(self, size=None):
        self.size = size if size is not None else [6000, 6000]
        self.surface = pygame.Surface(self.size)
        self.camera = Camera([300, 300], [600, 600], self.surface.get_rect(), [600, 600])
        self.sprite_group = pygame.sprite.Group()
        for i in range(1000):
            sprite = pygame.sprite.Sprite(self.sprite_group)
            sprite.image = pygame.Surface((20, 20)).convert_alpha()
            sprite.image.fill((255, 255, 255, 0))
            sprite.rect = sprite.image.get_rect()

            sprite.rect.topleft = [random.randrange(self.size[0]), random.randrange(self.size[1])]
            pygame.draw.circle(sprite.image,
                               (random.randint(0, 255),
                                random.randint(0, 255),
                                random.randint(0, 255)),
                               (10, 10), 10)

            # self.circle2 = pygame.draw.circle(self.surface, (0,200, 107), (200, 100), 30)

    def send_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.camera.zoom(1/.75)
            elif event.button == 5:
                self.camera.zoom(.75)

    def send_keys(self, pressed):
        if pressed[pygame.K_RIGHT]:
            self.camera.move([10, 0])
        if pressed[pygame.K_LEFT]:
            self.camera.move([-10, 0])
        if pressed[pygame.K_UP]:
            self.camera.move([0, -10])
        if pressed[pygame.K_DOWN]:
            self.camera.move([0, 10])

    def update(self):
        pass

    def render(self):
        self.sprite_group.draw(self.surface)

    def get_screen(self, size):
        return pygame.transform.scale(self.get_image(), size)

    def get_image(self, rect=None):
        if rect is None:
            rect = self.camera.get_rect()
        return self.surface.subsurface(rect)


if __name__ == '__main__':
    pygame.init()
    size = [800, 800]
    screen = pygame.display.set_mode(size)
    level = Level()
    running = True
    while running:
        pressed = pygame.key.get_pressed()
        level.send_keys(pressed)
        events = pygame.event.get()
        for event in events:
            level.send_event(event)
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    pass
        level.update()
        screen.fill((0, 0, 0))
        level.render()
        screen.blit(level.get_screen(size), (0, 0))
        pygame.display.flip()
