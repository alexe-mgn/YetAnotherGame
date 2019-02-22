import pygame
import random
from geometry import Vec2d, FRect


class SpriteGroup(pygame.sprite.Group):

    def update(self, time):
        for s in self.sprites():
            s.push_data(time)
            s.move_force(time)
            s.move_inertia(time)
            for _ in range(1):
                for cs in pygame.sprite.spritecollide(s, self, False):
                    if cs is not s:
                        s.collide(cs)
                s.handle_borders()
        for s in self.sprites():
            s.pull_data()
            s.apply_rect()

    def handle_collisions(self, group=None):
        if group is None:
            sa = sb = self.sprites()
        else:
            sa = self.sprites()
            sb = group.sprites()
        for a in sa:
            for b in sb:
                if a is not b:
                    if pygame.sprite.collide_rect(a, b):
                        a.collide(b)
                        # b.collide(a)

    def collisions(self):
        sprites = self.sprites()
        for na, a in enumerate(sprites[:-1]):
            for b in sprites[na + 1:]:
                if a != b:
                    if pygame.sprite.collide_rect(a, b):
                        yield [a, b]

    def collisions_dict(self):
        sprites = self.sprites()
        cols = {}
        for na, a in enumerate(sprites[:-1]):
            for b in sprites[na + 1:]:
                if a != b:
                    if pygame.sprite.collide_circle(a, b):
                        cols[a] = b
                        cols[b] = a
        return cols


class StaticObject(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.f_rect = FRect(self.rect)

        self.image = pygame.Surface((20, 20)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (0, 255, 0), (10, 10), 10)

        self.v = Vec2d(random.randrange(-50, 50), random.randrange(-50, 50))
        self.prev_time = 1000
        self.prev_pos = self.f_rect.center - self.v * (self.prev_time / 1000)

        self.force = Vec2d(0, 1000)

        self.mass = 1
        self.energy_coef = 1

    def collide(self, obj):
        oc, sc = Vec2d(obj.f_rect.center), Vec2d(self.f_rect.center)
        if oc == sc:
            return
        to_other = oc - sc
        d = Vec2d(to_other)
        d_len = (20 - to_other.length)
        if d_len > 0:
            d.length = d_len
            self.move(d * (-obj.mass / (self.mass + obj.mass) * self.energy_coef))
            obj.move(d * (self.mass / (self.mass + obj.mass) * obj.energy_coef))
        self.rect = self.f_rect.pygame

    def move(self, shift):
        return

    def update(self, time):
        return

    @property
    def pos(self):
        return self.f_rect.center

    @pos.setter
    def pos(self, p):
        center = self.f_rect.center
        shift = self.prev_pos - center
        self.f_rect.center = p
        self.prev_pos = p + shift
        # vel = self.f_rect.center - self.prev_pos
        # self.f_rect.center = p
        # self.prev_pos = p - vel
        self.rect = self.f_rect.pygame


class KinematicObject(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.f_rect = FRect(self.rect)

        self.image = pygame.Surface((20, 20)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (0, 200, 255), (10, 10), 10)

        self.v = Vec2d(random.randrange(-50, 50), random.randrange(-50, 50))
        self.prev_time = 1000
        self.prev_pos = self.f_rect.center - self.v * (self.prev_time / 1000)

        self.force = Vec2d(0, 000)

        self.mass = 1
        self.energy_coef = 1

    def collide(self, obj):
        oc, sc = Vec2d(obj.f_rect.center), Vec2d(self.f_rect.center)
        if oc == sc:
            return
        to_other = oc - sc
        d = Vec2d(to_other)
        d_len = (20 - to_other.length)
        if d_len > 0:
            d.length = d_len
            self.f_rect.center -= d * (obj.mass / (self.mass + obj.mass))
            obj.f_rect.center += d * (self.mass / (self.mass + obj.mass))
            p = to_other.perpendicular()
            self.elastic_collision(p)
            obj.elastic_collision(p)
        self.rect = self.f_rect.pygame

    def elastic_collision(self, wall_vector):
        vel_p = self.v.projection(wall_vector)
        vel_on = self.v.projection(wall_vector.perpendicular())
        pygame.draw.line(level.surface, (255, 0, 0), self.rect.center, self.rect.center + self.v, 2)
        self.v = (vel_p - vel_on) * self.energy_coef
        pygame.draw.line(level.surface, (0, 0, 255), self.rect.center, self.rect.center + self.v, 2)

    def update(self, time):
        center = self.f_rect.center
        prev_pos = Vec2d(center)
        self.v += self.force * ((time / 1000) / self.mass)
        self.f_rect.move_ip(*self.v * (time / 1000))
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


class DynamicObject(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        size = 100
        self.rect = pygame.Rect(0, 0, size, size)
        self.f_rect = FRect(self.rect)

        self.image = pygame.Surface((size, size)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (0, 255, 0), (size // 2, size // 2), size // 2)

        self.v = Vec2d(random.randrange(-50, 50), random.randrange(-50, 50))
        self.prev_time = 1000
        self.prev_pos = self.f_rect.center - self.v * (self.prev_time / 1000)

        self.force = Vec2d(0, 000)

        self.mass = 1
        self.energy_coef = 1

    def collide(self, obj):
        oc, sc = Vec2d(obj.f_rect.center), Vec2d(self.f_rect.center)
        if oc == sc:
            return
        to_other = oc - sc
        d = Vec2d(to_other)
        d_len = (100 - to_other.length)
        if d_len > 0:
            d.length = d_len
            self.move(d * (-obj.mass / (self.mass + obj.mass) * self.energy_coef))
            obj.move(d * (self.mass / (self.mass + obj.mass) * obj.energy_coef))
        self.rect = self.f_rect.pygame

    def handle_borders(self):
        d = 50
        if self.f_rect.centery < d:
            self.f_rect.centery = d
        if self.f_rect.centery > level.size[1] - d:
            self.f_rect.centery = level.size[1] - d
        if self.f_rect.centerx < d:
            self.f_rect.centerx = d
        if self.f_rect.centerx > level.size[0] - d:
            self.f_rect.centerx = level.size[0] - d

    def move(self, shift):
        self.f_rect.topleft += shift

    def update(self, time):
        pass

    def move_inertia(self, time):
        vel = (self.f_rect.center - self.prev_pos) * (time / self.prev_time)
        self.f_rect.move_ip(*(
                vel
        ))

    def move_force(self, time):
        self.f_rect.move_ip(*(
                self.force * (time**2 / 2000000)
        ))

    def push_data(self, time):
        self._temp = [Vec2d(self.f_rect.center), time]

    def pull_data(self):
        self.prev_pos, self.prev_time = self._temp

    def apply_rect(self):
        self.rect = self.f_rect.pygame

    @property
    def pos(self):
        return self.f_rect.center

    @pos.setter
    def pos(self, p):
        center = self.f_rect.center
        shift = self.prev_pos - center
        self.f_rect.center = p
        self.prev_pos = p + shift
        # vel = self.f_rect.center - self.prev_pos
        # self.f_rect.center = p
        # self.prev_pos = p - vel
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
        self.sprite_group = SpriteGroup()
        for i in range(10):
            sprite = DynamicObject(self.sprite_group)
            sprite.pos = (random.randrange(self.size[0]), random.randrange(self.size[1]))

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
            if event.key == pygame.K_n:
                self.upd = True
                self.update(10)
                self.upd = False

    def send_keys(self, pressed):
        if pressed[pygame.K_RIGHT]:
            self.camera.move_smooth([1, 0])
        if pressed[pygame.K_LEFT]:
            self.camera.move_smooth([-1, 0])
        if pressed[pygame.K_UP]:
            self.camera.move_smooth([0, -1])
        if pressed[pygame.K_DOWN]:
            self.camera.move_smooth([0, 1])
        self.upd = not pressed[pygame.K_SPACE]
        if pressed[pygame.K_b]:
            self.upd = True
            self.update(1)
            self.upd = False

    def update(self, time):
        if self.upd:
            self.camera.update(time)
            self.surface.set_clip(self.camera.get_rect())
            self.surface.fill((0, 0, 0))
            self.sprite_group.update(time)
            # self.sprite_group.handle_collisions()

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
    level = Level(screen_size=size, size=[800, 600])
    clock = pygame.time.Clock()
    timer = pygame.time.set_timer(29, 100)
    running = True
    t = None
    while running:
        ms = pygame.mouse.get_pos()
        pressed = pygame.key.get_pressed()
        level.send_keys(pressed)
        events = pygame.event.get()
        time = clock.tick()
        if time > 10:
            time = 10
        for event in events:
            level.send_event(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    pass
                elif event.button == 1:
                    if t is None:
                        for s in level.sprite_group.sprites():
                            if s.rect.collidepoint(event.pos):
                                t = s
                    else:
                        t = None
            elif event.type == 29:
                pygame.display.set_caption('FPS %d' % (1000 // time,))
        if t is not None:
            t.f_rect.center = ms
        screen.fill((0, 0, 0))
        level.update(time)
        level.render()
        screen.blit(level.get_screen(), (0, 0))
        pygame.display.flip()
