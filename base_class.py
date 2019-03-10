import pygame
import random
from geometry import Vec2d, FRect, Polygon, Circle
import math


class CameraGroup(pygame.sprite.Group):

    def draw(self, surface, camera):
        cam_rect = camera.c_rect
        cam_tl = cam_rect.topleft
        zoom = camera.get_current_zoom()
        blit = surface.blit
        for sprite in self.sprites():
            s_rect = sprite.rect
            s_tl = s_rect.topleft
            c_rect = s_rect.copy()
            c_rect.size = [e * zoom for e in s_rect.size]
            c_rect.topleft = [(s_tl[0] - cam_tl[0]) * zoom, (s_tl[1] - cam_tl[1]) * zoom]
            self.spritedict[sprite] = blit(pygame.transform.scale(sprite.read_image(), c_rect.size), c_rect)
        self.lostsprites = []


class PhysicsGroup(CameraGroup):
    
    def update(self, upd_time):
        for s in self.sprites():
            s.start_step()
            for cs in pygame.sprite.spritecollide(s, self, False):
                if cs is not s:
                    s.collide(cs)
            s.handle_borders()
        for s in self.sprites():
            s.pre_update(upd_time)
            s.update(upd_time)
            s.end_step()


class StaticObject(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        size = 100
        self.rect = pygame.Rect(0, 0, size, size)
        self.f_rect = FRect(self.rect)
        self.center = self.f_rect.center
        self.angle = 0

        self._i_image = pygame.Surface((size, size)).convert_alpha()
        self._i_image.fill((0, 0, 0, 0))
        pygame.draw.circle(self._i_image, (255, 255, 255), (size // 2, size // 2), size // 2)

        # Initial and real-time shape
        self._i_shape = Circle(self.center, size // 2)
        self._shape = self._i_shape

        self._vel = Vec2d(0, 0)
        self._a_vel = 0
        self.force = Vec2d(0, 0)
        self.torque = 0

        self.mass = 1
        self.inertia = self.mass
        self.bounce_coef = 100
        self.lose_coef = .998

    def get_shape(self):
        # self.shape.center = self.f_rect.center
        return self._shape

    def set_shape(self, shape):
        self._i_shape = shape
        self._shape = self._i_shape.rotated(self.angle)
        self._shape.center = self.center
    shape = property(get_shape, set_shape)

    def get_image(self):
        return self._i_image

    def read_image(self):
        img = pygame.transform.rotate(self._i_image, -self.angle)
        size = img.get_size()
        rect = pygame.Rect(0, 0, 0, 0)
        rect.center = (size[0] // 2, size[1] // 2)
        rect.inflate_ip(*self.f_rect.size)
        return img.subsurface(rect)

    def set_image(self, surf):
        self._i_image = surf
    image = property(get_image, set_image)

    def handle_borders(self):
        pass

    def collide(self, obj):
        cd = self.get_shape().collision_data(obj.get_shape())
        if cd[1]:
            # Collision detected
            cd2 = (cd[0], cd[1], -cd[2], cd[3] - cd[2])
            # Tell each other about collision
            self.effect(obj, cd)
            obj.effect(self, cd2)
            # Don't do anything with static, but obj should respond to collision.
            obj.collide_respond(self, cd2)

    def collide_respond(self, obj, c_data):
        pass

    def effect(self, obj, c_data):
        pass

    def pre_update(self, upd_time):
        pass

    def update(self, upd_time):
        # Move self, change velocity depending on force and lose_coef
        self.f_rect.move_ip(*(self._vel * (upd_time / 1000) + self.force * ((upd_time ** 2 / 2000000) / self.mass)))
        self._vel += self.force * ((upd_time / 1000) / self.mass)
        self._vel *= self.lose_coef
        # Same with angular values
        da = self._a_vel * (upd_time / 1000)
        self.angle += da
        self._a_vel += self.torque * ((upd_time / 1000) * (.1 / self.inertia) * (.180 / math.pi))
        self._a_vel *= self.lose_coef

    def apply_force(self, f, point=None):
        pass

    def move(self, shift):
        self.f_rect.move_ip(*shift)

    def start_step(self):
        pass

    def end_step(self):
        # Apply floating point precision rectangle to one, that pygame reads for drawing.
        self.rect = self.f_rect.pygame
        self.center = self.f_rect.center
        # Update shape
        self._shape = self._i_shape.rotated(self.angle)
        self._shape.center = self.center
        # Zero forces
        self.force[0], self.force[1] = 0, 0
        self.torque = 0

    @property
    def pos(self):
        return self.center

    @pos.setter
    def pos(self, p):
        self.f_rect.center = p
        self.rect = self.f_rect.pygame
        self._shape.center = p

    @property
    def velocity(self):
        return self._vel

    @velocity.setter
    def velocity(self, vel):
        self._vel[0], self._vel[1] = vel[0], vel[1]


class PhysObject(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)
        size = 100
        self.rect = pygame.Rect(0, 0, size, size)
        self.f_rect = FRect(self.rect)
        self.center = self.f_rect.center
        self.angle = 0

        self._i_image = pygame.Surface((size, size)).convert_alpha()
        self._i_image.fill((0, 0, 0, 0))
        pygame.draw.circle(self._i_image, (0, 0, 255), (size // 2, size // 2), size // 2)

        self._i_shape = Circle(self.center, size // 2)
        self._shape = self._i_shape

        self._vel = Vec2d(random.randrange(-50, 50), random.randrange(-50, 50))
        self._a_vel = 45
        self.force = Vec2d(0, 0)
        self.torque = 0

        self.mass = 1
        self.inertia = self.mass
        self.bounce_coef = 100
        self.lose_coef = .998

    def get_shape(self):
        return self._shape

    def set_shape(self, shape):
        self._i_shape = shape
        self._shape = self._i_shape.rotated(self.angle)
        self._shape.center = self.center
    shape = property(get_shape, set_shape)

    def get_image(self):
        return self._i_image

    def read_image(self):
        img = pygame.transform.rotate(self._i_image, -self.angle)
        size = img.get_size()
        rect = pygame.Rect(0, 0, 0, 0)
        rect.center = (size[0] // 2, size[1] // 2)
        rect.inflate_ip(*self.f_rect.size)
        return img.subsurface(rect)

    def set_image(self, surf):
        self._i_image = surf
    image = property(get_image, set_image)

    def handle_borders(self):
        d = 10
        if self.center[1] < d:
            # self.f_rect.centery = d
            self._vel[1] = abs(self._vel[1])
        if self.center[1] > level.size[1] - d:
            # self.f_rect.centery = level.size[1] - d
            self._vel[1] = -abs(self._vel[1])
        if self.center[0] < d:
            # self.f_rect.centerx = d
            self._vel[0] = abs(self._vel[0])
        if self.center[0] > level.size[0] - d:
            # self.f_rect.centerx = level.size[0] - d
            self._vel[0] = -abs(self._vel[0])

    def collide(self, obj):
        cd = self.get_shape().collision_data(obj.get_shape())
        if cd[1]:
            # Collision detected
            cd2 = (cd[0], cd[1], -cd[2], cd[3] - cd[2])
            # Tell each other about collision
            self.effect(obj, cd)
            obj.effect(self, cd2)
            # Resolve collision
            f = cd[2] * (-self.bounce_coef - obj.bounce_coef)
            self.apply_force(f, cd[3])
            obj.collide_respond(self, cd2)

    def collide_respond(self, obj, c_data):
        self.apply_force(c_data[2] * (-self.bounce_coef - obj.bounce_coef), c_data[3])

    def effect(self, obj, c_data):
        pass

    def pre_update(self, upd_time):
        pass

    def update(self, upd_time):
        # Move self, change velocity depending on force and lose_coef
        self.f_rect.move_ip(*(self._vel * (upd_time / 1000) + self.force * ((upd_time ** 2 / 2000000) / self.mass)))
        self._vel += self.force * ((upd_time / 1000) / self.mass)
        self._vel *= self.lose_coef
        # Same with angular values
        da = self._a_vel * (upd_time / 1000)
        self.angle += da
        self._a_vel += self.torque * ((upd_time / 1000) * (.1 / self.inertia) * (.180 / math.pi))
        self._a_vel *= self.lose_coef

    def apply_force(self, f, point=None):
        # Apply force to center of mass
        f = Vec2d(f)
        self.force += f
        if point is not None:
            # And calculate torque if point is not mass center
            to_p = point - self.center
            self.torque += to_p.cross(f)

    def move(self, shift):
        self.f_rect.move_ip(*shift)

    def start_step(self):
        pass

    def end_step(self):
        # Apply floating point precision rectangle to one, that pygame reads for drawing.
        self.rect = self.f_rect.pygame
        self.center = self.f_rect.center
        # Update shape
        self._shape = self._i_shape.rotated(self.angle)
        self._shape.center = self.center
        # Zero forces
        self.force[0], self.force[1] = 0, 0
        self.torque = 0

    @property
    def pos(self):
        return self.center

    @pos.setter
    def pos(self, p):
        self.f_rect.center = p
        self.rect = self.f_rect.pygame
        self._shape.center = p
    
    @property
    def velocity(self):
        return self._vel

    @velocity.setter
    def velocity(self, vel):
        self._vel[0], self._vel[1] = vel[0], vel[1]


class Camera:

    def __init__(self, center, size, constraint, zoom_con=None):
        self._constraint = pygame.Rect(constraint)
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
        self.rect.clamp_ip(self._constraint)

        self.c_rect = FRect(self.rect)

    def update(self, upd_time):
        tc, cc = self.rect.center, self.c_rect.center
        ts, cs = self.rect.size, self.c_rect.size
        dis_x, dis_y = tc[0] - cc[0], tc[1] - cc[1]
        ds_x, ds_y = ts[0] - cs[0], ts[1] - cs[1]

        if abs(ds_x) < .5:
            self.c_rect.w = ts[0]
        else:
            self.c_rect.w += ds_x * self.zoom_speed * upd_time / 1000
        if abs(ds_y) < .5:
            self.c_rect.h = ts[1]
        else:
            self.c_rect.h += ds_y * self.zoom_speed * upd_time / 1000

        if abs(dis_x) < .5:
            self.c_rect.centerx = tc[0]
        else:
            self.c_rect.centerx = cc[0] + dis_x * self.move_speed * upd_time / 1000
        if abs(dis_y) < .5:
            self.c_rect.centery = tc[1]
        else:
            self.c_rect.centery = cc[1] + dis_y * self.move_speed * upd_time / 1000
        self.c_rect.clamp_ip(self._constraint)

    def get_rect(self):
        rect = pygame.Rect(0, 0, 0, 0)
        rect.center = self.c_rect.center
        rect.inflate_ip(self.c_rect.width // 2 * 2, self.c_rect.height // 2 * 2)
        return rect

    def move(self, shift):
        self.rect.x += shift[0]
        self.rect.y += shift[1]
        self.rect.clamp_ip(self._constraint)

    def move_smooth(self, coef):
        self.rect.x += self.c_rect.width * coef[0] / 100
        self.rect.y += self.c_rect.height * coef[1] / 100
        self.rect.clamp_ip(self._constraint)

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
        if premade[0] > self._constraint.size[0] or premade[1] > self._constraint.size[1]:
            m_ind = min((0, 1), key=lambda e: self._constraint.size[e] - premade[e])
            self.set_zoom(self.i_size[m_ind] / self._constraint.size[m_ind])
            return
        self.rect.size = premade
        self.rect.center = center
        self.rect.clamp_ip(self._constraint)
        self._zoom = zoom
    zoom = property(get_zoom, set_zoom)

    def get_current_zoom(self):
        return self.i_size[0] / self.c_rect.width

    @property
    def center(self):
        return self.rect.center

    @center.setter
    def center(self, pos):
        self.rect.center = pos

    def get_constraint(self):
        return self._constraint

    def set_constraint(self, rect):
        self._constraint = rect
        self.set_zoom(self.get_zoom())
    constraint = property(get_constraint, set_constraint)

    def get_size(self):
        return self.i_size

    def set_size(self, size):
        self.i_size = size
        self.set_zoom(self.get_zoom())
    size = property(get_size, set_size)


class Level:

    def __init__(self, size=None, screen_size=None):
        self.size = size if size is not None else [6000, 6000]
        self.screen_size = screen_size if screen_size is not None else [600, 600]
        self.update_rect = pygame.Rect(0, 0, *self.size)

        self.camera = Camera([300, 300], self.screen_size, self.get_rect(), [None, 4])
        self.visible = self.camera.get_rect()

        self.sprites = PhysicsGroup()
        self.pregenerate()

    def pregenerate(self):
        pass

    def send_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.camera.zoom /= .75
            elif event.button == 5:
                self.camera.zoom *= .75
        elif event.type == pygame.VIDEORESIZE:
            self.screen_size = event.size
            self.camera.size = event.size

    def send_keys(self, pressed):
        if pressed[pygame.K_RIGHT]:
            self.camera.move_smooth([1, 0])
        if pressed[pygame.K_LEFT]:
            self.camera.move_smooth([-1, 0])
        if pressed[pygame.K_UP]:
            self.camera.move_smooth([0, -1])
        if pressed[pygame.K_DOWN]:
            self.camera.move_smooth([0, 1])

    def start_step(self):
        pass

    def update(self, upd_time):
        self.camera.update(upd_time)
        self.visible = self.camera.get_rect()
        self.sprites.update(upd_time)

    def draw(self, surface):
        self.sprites.draw(surface, self.camera)

    def end_step(self):
        pass

    def get_rect(self):
        return pygame.Rect(0, 0, *self.size)

    def get_mouse(self):
        ms = pygame.mouse.get_pos()
        sc, vs = self.screen_size, self.visible.size
        zoom = max((sc[0] / vs[0], sc[1] / vs[1]))
        return Vec2d(ms) / zoom + self.visible.topleft


if __name__ == '__main__':

    class Test(Level):

        def __init__(self, size=None, screen_size=None):
            super().__init__(size, screen_size)
            self.size = size if size is not None else [6000, 6000]
            self.screen_size = screen_size if screen_size is not None else [600, 600]
            self.surface = pygame.Surface(self.size)
            self.update_rect = self.surface.get_rect()

            self.camera = Camera([300, 300], self.screen_size, self.surface.get_rect(), [None, 4])
            self.visible = self.camera.get_rect()

            self.sprites = PhysicsGroup()
            self.upd = True

            for i in range(10):
                sprite = PhysObject(self.sprites)
                sprite.pos = (random.randrange(self.size[0]), random.randrange(self.size[1]))
            sprite = PhysObject(self.sprites)
            sprite.shape = Polygon(FRect(0, 0, 200, 10))
            sprite.f_rect = FRect(sprite.shape.maximum_bounding(return_pygame=True))
            sprite.image = pygame.Surface(sprite.f_rect.size).convert_alpha()
            sprite.image.fill((255, 255, 255, 0))
            fs = sprite.image.get_size()
            sprite.shape.centered((fs[0] / 2, fs[1] / 2)).draw(sprite.image, color=(255, 0, 0), width=0)
            self.unique = sprite

        def send_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.camera.zoom *= 1 / .75
                elif event.button == 5:
                    self.camera.zoom /= 1 / .75
            elif event.type == pygame.VIDEORESIZE:
                self.screen_size = event.size
                self.camera.size = event.size
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
            if pressed[pygame.K_j]:
                for s in self.sprites.sprites():
                    s.velocity = [0, 0]

    pygame.init()
    size = [800, 600]
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    level = Test(screen_size=size, size=size)
    clock = pygame.time.Clock()
    timer = pygame.time.set_timer(29, 100)
    running = True
    t = None
    while running:
        ms = level.get_mouse()
        pressed = pygame.key.get_pressed()
        level.send_keys(pressed)
        events = pygame.event.get()
        upd_time = clock.tick()
        if not 0 < upd_time < 10:
            upd_time = 1
        for event in events:
            level.send_event(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                size = event.size
                pygame.display.set_mode(size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if t is None:
                        for s in level.sprites.sprites():
                            if s.rect.collidepoint(ms):
                                t = s
                                t.velocity = [0, 0]
                                break
                    else:
                        t.velocity = (Vec2d(ms) - prev_ms) * (1000 / upd_time)
                        t = None
                elif t is not None:
                    if event.button == 5:
                        t.mass -= 1
                    elif event.button == 4:
                        t.mass += 1
            elif event.type == 29:
                pygame.display.set_caption('FPS %d' % (1000 // upd_time,))
        if t is not None:
            t.velocity = [0, 0]
            t.pos = ms

        screen.fill((0, 0, 0))
        level.update(upd_time)
        level.draw(screen)
        pygame.display.flip()
        prev_ms = ms
