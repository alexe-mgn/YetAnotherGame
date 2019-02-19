import pygame
import random
from geometry import FRect


class Camera:

    def __init__(self, size, constraint, zoom_con=None):
        self.constraint = pygame.Rect(constraint)
        self.size = list(size)

        if zoom_con is None:
            self.zoom_con = [None, None]
        else:
            self.zoom_con = zoom_con
        self._zoom = 1
        if self.zoom_con[0] is not None and self._zoom < self.zoom_con[0]:
            self._zoom = self.zoom_con[0]
        if self.zoom_con[1] is not None and self._zoom > self.zoom_con[1]:
            self._zoom = self.zoom_con[1]

        self.move_speed = 6
        self.zoom_speed = 2

        self.rect = FRect(0, 0, *self.size)
        self.rect.clamp_ip(self.constraint)

        self.c_rect = FRect(self.rect)

    def update(self, time):
        tc, cc = self.rect.center, self.c_rect.center
        ts, cs = self.rect.size, self.c_rect.size
        dis_x, dis_y = tc[0] - cc[0], tc[1] - cc[1]
        ds_x, ds_y = ts[0] - cs[0], ts[1] - cs[1]

        if abs(ds_x) < .5:
            self.c_rect.w = ts[0]
        else:
            self.c_rect.w += ds_x * self.zoom_speed * time / 1000
        if abs(ds_y) < .5:
            self.c_rect.h = ts[1]
        else:
            self.c_rect.h += ds_y * self.zoom_speed * time / 1000

        if abs(dis_x) < .5:
            self.c_rect.centerx = tc[0]
        else:
            self.c_rect.centerx = cc[0] + dis_x * self.move_speed * time / 1000
        if abs(dis_y) < .5:
            self.c_rect.centery = tc[1]
        else:
            self.c_rect.centery = cc[1] + dis_y * self.move_speed * time / 1000
        self.c_rect.clamp_ip(self.constraint)

    def get_rect(self):
        rect = pygame.Rect(0, 0, 0, 0)
        rect.center = self.c_rect.center
        rect.inflate_ip(self.c_rect.width // 2 * 2, self.c_rect.height // 2 * 2)
        return rect

    def move(self, shift):
        self.rect.x += shift[0]
        self.rect.y += shift[1]
        self.rect.clamp_ip(self.constraint)

    def move_smooth(self, coef):
        self.rect.x += self.c_rect.width * coef[0] / 100
        self.rect.y += self.c_rect.height * coef[1] / 100
        self.rect.clamp_ip(self.constraint)

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, zoom):
        if zoom <= 0:
            return
        center = self.rect.center
        if self.zoom_con[0] is not None and zoom < self.zoom_con[0]:
            zoom = self.zoom_con[0]
        if self.zoom_con[1] is not None and zoom > self.zoom_con[1]:
            zoom = self.zoom_con[1]
        premade = [self.size[0] / zoom, self.size[1] / zoom]
        if premade[0] > self.constraint.size[0] or premade[1] > self.constraint.size[1]:
            return
        self.rect.size = premade
        self.rect.center = center
        self.rect.clamp_ip(self.constraint)
        self._zoom = zoom

    @property
    def center(self):
        return self.rect.center

    @center.setter
    def center(self, pos):
        self.rect.center = pos


class Level:

    def __init__(self, size=None, screen_size=None):
        self.size = size if size is not None else [6000, 6000]
        self.screen_size = screen_size if screen_size is not None else [600, 600]
        self.camera = Camera(self.screen_size, [0, 0, *self.size], [None, 4])
        self.sprite_group = CamSpriteGroup()
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
                self.camera.zoom /= .75
            elif event.button == 5:
                self.camera.zoom *= .75
        elif event.type == pygame.VIDEORESIZE:
            self.screen_size = event.size
            self.camera.screen_size = self.screen_size
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.camera.rect.center = [e // 2 for e in self.size]

    def send_keys(self, pressed):
        if pressed[pygame.K_RIGHT]:
            self.camera.move_smooth([1, 0])
        if pressed[pygame.K_LEFT]:
            self.camera.move_smooth([-1, 0])
        if pressed[pygame.K_UP]:
            self.camera.move_smooth([0, -1])
        if pressed[pygame.K_DOWN]:
            self.camera.move_smooth([0, 1])

    def update(self, time):
        self.camera.update(time)
        self.sprite_group.update(time)

    def draw(self, surface):
        self.sprite_group.draw(surface, self.camera)


class CamSpriteGroup(pygame.sprite.Group):

    def draw(self, surface, camera):
        sprites = self.sprites()
        cam_rect = camera.c_rect
        cam_tl = cam_rect.topleft
        zoom = camera.size[0] / cam_rect.size[0]
        blit = surface.blit
        for sprite in sprites:
            s_rect = sprite.rect
            s_tl = s_rect.topleft
            c_rect = s_rect.copy()
            c_rect.size = [e * zoom for e in s_rect.size]
            c_rect.topleft = [(s_tl[0] - cam_tl[0]) * zoom, (s_tl[1] - cam_tl[1]) * zoom]
            self.spritedict[sprite] = blit(pygame.transform.scale(sprite.image, c_rect.size), c_rect)
        self.lostsprites = []


if __name__ == '__main__':
    pygame.init()
    size = [900, 600]
    screen = pygame.display.set_mode(size)
    level = Level(screen_size=size)
    clock = pygame.time.Clock()
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
        level.update(clock.tick())
        screen.fill((0, 0, 0))
        level.draw(screen)
        pygame.display.flip()
