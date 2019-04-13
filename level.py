import pygame
from geometry import Vec2d, FRect


class Camera:

    def __init__(self, center, screen_rect, constraint, zoom_con=None, zoom_offset=1):
        self._constraint = pygame.Rect(constraint)
        self.i_size = list(screen_rect.size)

        if zoom_con is None:
            self.zoom_con = [None, None]
        else:
            self.zoom_con = zoom_con
        self.zoom_offset = zoom_offset
        self._zoom = 1 / zoom_offset
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
        self.zoom = 1

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
        return self.c_rect
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
        return self._zoom * self.zoom_offset

    def set_zoom(self, zoom):
        zoom = zoom / self.zoom_offset
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
        self._constraint = pygame.Rect(rect)
        self.set_zoom(self.get_zoom())
    constraint = property(get_constraint, set_constraint)

    def move_constraint(self, rect):
        self._constraint = pygame.Rect(rect)
        self.rect.clamp_ip(self._constraint)

    def get_size(self):
        return self.i_size

    def set_size(self, size):
        self.i_size = size
        self.set_zoom(self.get_zoom())
    size = property(get_size, set_size)

    def world_to_local(self, pos):
        rect = self.get_rect()
        tl = rect.topleft
        zoom = self.get_current_zoom()
        return (Vec2d(pos) - tl) * zoom

    def local_to_world(self, pos):
        rect = self.get_rect()
        tl = rect.topleft
        zoom = self.get_current_zoom()
        return Vec2d(pos) / zoom + tl


class Level:

    def __init__(self, size=None, screen=None, zoom_offset=1):
        self.size = size if size is not None else [6000, 6000]
        self.screen = pygame.Rect(screen if screen is not None else [0, 0, 800, 600])
        self.update_rect = pygame.Rect(0, 0, *self.size)

        self.camera = Camera((0, 0), self.screen, self.get_rect(), [None, 4], zoom_offset=zoom_offset)
        self.visible = self.camera.get_rect()

        self.player = None
        self.step_time = 1
        self.space_time_coef = 1
        self.phys_group = None
        self.gui = None
        self.pressed = []
        self.mouse_relative_prev = Vec2d(0, 0)
        self.mouse_absolute_prev = Vec2d(0, 0)
        self.mouse_relative = Vec2d(0, 0)
        self.mouse_absolute = Vec2d(0, 0)
        self.pregenerate()

    def pregenerate(self):
        pass

    def send_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.camera.zoom /= .75
            elif event.button == 5:
                self.camera.zoom *= .75
        if self.gui is not None:
            self.gui.send_event(event)

    def set_screen(self, rect, offset=1):
        rect = pygame.Rect(rect)
        self.screen = rect
        self.camera.zoom_offset = offset
        self.camera.size = rect.size
        self.update_group_draw()

    def update_group_draw(self):
        if self.phys_group is not None:
            self.phys_group.draw_offset = self.screen.topleft
        if self.gui is not None:
            self.gui.rect = (0, 0, 100, 100)
            self.gui.absolute = False

    def world_to_local(self, pos):
        return self.camera.world_to_local(pos)

    def local_to_world(self, pos):
        return self.camera.local_to_world(pos)

    def handle_keys(self):
        pressed = self.pressed
        if pressed[pygame.K_RIGHT]:
            self.camera.move_smooth([1, 0])
        if pressed[pygame.K_LEFT]:
            self.camera.move_smooth([-1, 0])
        if pressed[pygame.K_UP]:
            self.camera.move_smooth([0, -1])
        if pressed[pygame.K_DOWN]:
            self.camera.move_smooth([0, 1])
        if self.player is not None:
            self.player.walk((
                int(pressed[pygame.K_d]) - int(pressed[pygame.K_a]),
                int(pressed[pygame.K_s]) - int(pressed[pygame.K_w])
            ))

    def start_step(self, upd_time, time_coef=1):
        self.step_time = upd_time * time_coef
        self.pressed = pygame.key.get_pressed()
        self.mouse_relative_prev = self.mouse_relative
        self.mouse_absolute_prev = self.mouse_absolute
        self.mouse_relative = Vec2d(pygame.mouse.get_pos())
        self.mouse_absolute = self.get_mouse()
        if self.player is not None:
            self.player.angle = (self.mouse_absolute - self.player.pos).angle
        if self.gui is not None:
            self.gui.start_step(upd_time)

    def end_step(self):
        if self.gui is not None:
            self.gui.end_step()

    def update(self):
        self.camera.update(self.step_time)
        self.visible = self.camera.get_rect()
        if self.phys_group is not None:
            self.phys_group.update(self.step_time * self.space_time_coef)
        if self.gui is not None:
            self.gui.update()

    def draw(self, surface):
        if self.phys_group is not None:
            self.phys_group.draw(surface, self.camera)
        if self.gui is not None:
            self.gui.draw(surface)

    def get_rect(self):
        return pygame.Rect(0, 0, *self.size)

    def get_mouse(self):
        ms = pygame.mouse.get_pos()
        sc, vs = self.screen.size, self.visible.size
        zoom = max((sc[0] / vs[0], sc[1] / vs[1]))
        return (Vec2d(ms) - self.screen.topleft) / zoom + self.visible.topleft
