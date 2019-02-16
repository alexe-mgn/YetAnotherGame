import pygame
import random
from geometry import Vec2d, FRect


class PhysObject(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = pygame.Rect(10, 10, 50, 50)
        self.f_rect = FRect(self.rect)
        self.image = pygame.Surface((50, 50)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (255, 255, 255), (25, 25), 10)
        self.v = Vec2d(random.randrange(-50, 50),random.randrange(-50, 50))
        self.prev_pos = self.f_rect.center - self.v

    def collide(self, obj):
        pass

    def update(self, time):
        prev_pos = Vec2d(self.f_rect.center)
        # self.f_rect.move_ip((self.f_rect.center[0] - self.prev_pos[0]) * time / 1000,
        #                     (self.f_rect.center[1] - self.prev_pos[1]) * time / 1000)
        self.f_rect.move_ip(*((-self.prev_pos + self.f_rect.center)))
        self.prev_pos = prev_pos
        self.rect = self.f_rect.pygame

    @property
    def pos(self):
        return self.f_rect.center

    @pos.setter
    def pos(self, p):
        vel = self.f_rect.center - self.prev_pos
        self.f_rect.center = p
        self.prev_pos = p - vel
        self.rect = self.f_rect.pygame


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

        self.move_speed = 6
        self.zoom_speed = 2

        self.rect = FRect(0, 0, *self.i_size)
        self.rect.center = center
        self.rect.clamp_ip(self.constraint)

        self.c_rect = FRect(self.rect)

    def update(self, time):
        tc, cc = self.rect.center, self.c_rect.center
        ts, cs = self.rect.size, self.c_rect.size
        dis_x, dis_y = tc[0] - cc[0], tc[1] - cc[1]
        ds_x, ds_y = ts[0] - cs[0], ts[1] - cs[1]

        if abs(ds_x) < 2:
            self.c_rect.w = ts[0]
        else:
            self.c_rect.w += ds_x * self.zoom_speed * time / 1000
        if abs(ds_y) < 2:
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
            sprite = PhysObject(self.sprite_group)
            sprite.pos = (random.randrange(self.size[0]),random.randrange(self.size[1]))

    def send_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.camera.zoom *= 1 / .75
            elif event.button == 5:
                self.camera.zoom /= 1 / .75
        elif event.type == pygame.VIDEORESIZE:
            self.screen_size = event.size
            # Camera update needed
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.camera.rect.make_int()

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
        self.surface.set_clip(self.camera.get_rect())
        self.surface.fill((0, 0, 0))
        self.sprite_group.update(time)

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
        level.render()
        screen.blit(level.get_screen(), (0, 0))
        pygame.display.flip()
