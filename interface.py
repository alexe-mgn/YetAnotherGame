import pygame
import pymunk
from geometry import Vec2d, FRect


class Camera:

    def __init__(self, center, size, constraint, zoom_con=None, zoom_offset=1):
        self._constraint = pygame.Rect(constraint)
        self.i_size = list(size)

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


class Level:

    def __init__(self, size=None, screen_size=None, zoom_offset=1):
        self.size = size if size is not None else [6000, 6000]
        self.screen_size = screen_size if screen_size is not None else [600, 600]
        self.update_rect = pygame.Rect(0, 0, *self.size)

        self.camera = Camera((0, 0), self.screen_size, self.get_rect(), [None, 4], zoom_offset=zoom_offset)
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

    def set_screen_size(self, size, offset=1):
        self.screen_size = size
        self.camera.zoom_offset = offset
        self.camera.size = size

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
        if self.player:
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
        if self.player:
            self.player.angle = (self.mouse_absolute - self.player.pos).angle

    def end_step(self):
        pass

    def update(self):
        self.camera.update(self.step_time)
        self.visible = self.camera.get_rect()
        if self.phys_group:
            self.phys_group.update(self.step_time * self.space_time_coef)
        if self.gui:
            self.gui.update()

    def draw(self, surface):
        if self.phys_group:
            self.phys_group.draw(surface, self.camera)
        if self.gui:
            self.gui.draw(surface)

    def get_rect(self):
        return pygame.Rect(0, 0, *self.size)

    def get_mouse(self):
        ms = pygame.mouse.get_pos()
        sc, vs = self.screen_size, self.visible.size
        zoom = max((sc[0] / vs[0], sc[1] / vs[1]))
        return Vec2d(ms) / zoom + self.visible.topleft


class Menu:

    def __init__(self):
        self.image = None
        self.elements = []

    def __iter__(self):
        return self.elements

    def __getitem__(self, ind):
        return self.elements[ind]

    def __setitem__(self, ind, val):
        self.elements[ind] = val

    def __delitem__(self, ind):
        del self.elements[ind]

    def add(self, element):
        self.elements.append(element)

    def get_mouse_hits(self):
        ms = pygame.mouse.get_pos()
        hits = []
        for i in self.elements:
            if i.collidepoint(ms):
                hits.append(i)
        return hits

    def update(self):
        ms = pygame.mouse.get_pos()
        hits = self.get_mouse_hits()
        for i in self.elements:
            if i.collidepoint(ms):
                i.mouse_on()
            else:
                i.mouse_off()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in hits:
                        i.button_down()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for i in self.elements:
                        i.button_up()

    def draw(self, surface, rect=None):
        rect = pygame.Rect(rect if rect else surface.get_rect())
        if self.image:
            surface.blit(pygame.transform.scale(self.image, rect.size), rect)
        for i in self.elements:
            i.draw(surface, rect)


class Element:

    def __init__(self, menu=None):
        self.image = None
        self._rect = FRect(0, 0, 0, 0)
        self.hover = False
        self.press = False
        if menu:
            menu.add(self)

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect):
        self._rect = FRect(rect)

    def update(self):
        pass

    def collidepoint(self, pos):
        return self.rect.collidepoint(*pos)

    def mouse_on(self):
        self.hover = True

    def mouse_off(self):
        self.hover = False
        self.press = False

    def button_down(self):
        self.press = True

    def button_up(self):
        self.press = False

    def draw(self, surface, rect=None):
        rect = pygame.Rect(rect) if rect else surface.get_rect()
        tl = Vec2d(rect.topleft)
        sz = Vec2d(rect.size)
        s_rect = self.rect
        s_tl = Vec2d(s_rect.topleft)
        s_sz = Vec2d(s_rect.size)
        k = sz / 100
        if self.image:
            surface.blit(pygame.transform.scale(self.image, s_sz * k), tl + s_tl * k)
        else:
            pygame.draw.rect(surface, (255, 0, 0), (*(tl + s_tl * k), *(s_sz * k)), 1)


class Button(Element):
    pass


if __name__ == '__main__':
    from main_loop import Main
    import random
    main = Main()
    level = Level(screen_size=main.visible, zoom_offset=main.zoom_offset)
    menu = Menu()
    el = Element(menu)
    el.rect = (0, 0, 99.9, 50)
    level.gui = menu
    main.load_level(level)
    main.start()