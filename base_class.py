import pygame
import random
from geometry import FRect


class Camera:

    def __init__(self, center, size, constraint, zoom_con=None):
        self.constraint = pygame.Rect(constraint)
        self.i_size = list(size)
        if zoom_con is None:
            self.zoom_con = [None, None]
        else:
            self.zoom_con = zoom_con
        self._zoom = 1
        if self.zoom_con[0] is not None and self._zoom < self.zoom_con[0]:
            self._zoom = self.zoom_con[0]
        if self.zoom_con[1] is not None and self._zoom > self.zoom_con[1]:
            self._zoom = self.zoom_con[1]
        self.rect = FRect(0, 0, *size)
        self.rect.center = center
        self.rect.clamp_ip(self.constraint)

    def get_rect(self):
        return self.rect.pygame

    def move(self, shift):
        self.rect.x += shift[0]
        self.rect.y += shift[1]
        self.rect.clamp_ip(self.constraint)

    def move_smooth(self, coef):
        self.rect.x += self.rect.width * coef[0] / 100
        self.rect.y += self.rect.height * coef[1] / 100
        self.rect.clamp_ip(self.constraint)

    def get_zoom(self):
        return self._zoom

    def set_zoom(self, zoom):
        if zoom <= 0:
            return
        center = self.rect.center
        if self.zoom_con[0] is not None and zoom < self.zoom_con[0]:
            zoom = self.zoom_con[0]
        if self.zoom_con[1] is not None and zoom > self.zoom_con[1]:
            zoom = self.zoom_con[1]
        premade = [e / zoom for e in self.i_size]
        if premade[0] > self.constraint.size[0] or premade[1] > self.constraint.size[1]:
            return
        self.rect.size = premade
        self.rect.center = center
        self.rect.clamp_ip(self.constraint)
        self._zoom = zoom
    zoom = property(get_zoom, set_zoom)


class Level:

    def __init__(self, size=None, screen_size=None):
        self.size = size if size is not None else [6000, 6000]
        self.screen_size = screen_size if screen_size is not None else [600, 600]
        self.surface = pygame.Surface(self.size)
        self.camera = Camera([300, 300], self.screen_size, self.surface.get_rect(), [None, 4])
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
                self.camera.zoom *= 1 / .75
            elif event.button == 5:
                self.camera.zoom /= 1 / .75
        if event.type == pygame.VIDEORESIZE:
            self.screen_size = event.size
            # Camera update needed

    def send_keys(self, pressed):
        if pressed[pygame.K_RIGHT]:
            self.camera.move_smooth([1, 0])
        if pressed[pygame.K_LEFT]:
            self.camera.move_smooth([-1, 0])
        if pressed[pygame.K_UP]:
            self.camera.move_smooth([0, -1])
        if pressed[pygame.K_DOWN]:
            self.camera.move_smooth([0, 1])

    def update(self):
        pass

    def render(self):
        self.sprite_group.draw(self.surface)

    def get_screen(self):
        return pygame.transform.scale(self.get_image(), self.screen_size)

    def get_image(self, rect=None):
        if rect is None:
            rect = self.camera.get_rect()
        return self.surface.subsurface(rect)


if __name__ == '__main__':
    pygame.init()
    size = [800, 600]
    screen = pygame.display.set_mode(size)
    level = Level(screen_size=size)
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
        screen.blit(level.get_screen(), (0, 0))
        pygame.display.flip()
