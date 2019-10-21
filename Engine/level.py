from Engine.config import EVENT
from Engine.geometry import Vec2d, FRect

import pygame


class Camera:
    """
    Класс камеры. Содержит набор методов для выбора отображаемой области уровня, масштабирования.
    """
    def __init__(self, center, screen_rect, constraint, zoom_con=None, zoom_offset=1):
        """
        :param center: Начальная позиция камеры
        :param screen_rect: Прямоугольник отображаемой области c масштабированием 1, важен лишь размер
        :param constraint: Область, в которую камере разрешено заходить [x1, y1, x2, y2]
        :param zoom_con: Ограничения масштабирования. [min, max]
        :param zoom_offset:
        """
        self._constraint = pygame.Rect(constraint)
        self.i_size = list(screen_rect.size)
        self.screen_shift = list(screen_rect.topleft)

        if zoom_con is None:
            self.zoom_con = [None, None]
        else:
            self.zoom_con = zoom_con
        self.zoom_offset = zoom_offset
        self._target_zoom = 1 / zoom_offset
        if self.zoom_con[0] is not None and self._target_zoom < self.zoom_con[0]:
            self._target_zoom = self.zoom_con[0]
        if self.zoom_con[1] is not None and self._target_zoom > self.zoom_con[1]:
            self._target_zoom = self.zoom_con[1]

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
        # print(cs, self.zoom, self.zoom_offset, self.zoom / self.zoom_offset)
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
        """
        Прямоугольник в системе координат уровня, который камера освещает на данный момент..
        :return: Rect()
        """
        return self.c_rect
        # rect = pygame.Rect(0, 0, 0, 0)
        # rect.center = self.c_rect.center
        # rect.inflate_ip(self.c_rect.width // 2 * 2, self.c_rect.height // 2 * 2)
        # return rect

    def move(self, shift):
        """
        Сдвинуть камеру на вектор.
        :param shift: (x, y)
        """
        self.rect.x += shift[0]
        self.rect.y += shift[1]
        self.rect.clamp_ip(self._constraint)

    def move_smooth(self, coef):
        """
        Сдвиг камеры на процент текущего размера области отображения.
        :param coef: (x (%), y (%))
        :return:
        """
        self.rect.x += self.c_rect.width * coef[0] / 100
        self.rect.y += self.c_rect.height * coef[1] / 100
        self.rect.clamp_ip(self._constraint)

    def get_zoom(self):
        """
        Целевое масштабирование камеры.
        :return: int
        """
        return self._target_zoom * self.zoom_offset

    def set_zoom(self, zoom):
        """
        Установить целевое масштабирование камеры.
        :param zoom: int
        """
        # absolute zoom
        zoom = zoom / self.zoom_offset
        if zoom <= 0:
            return
        center = self.rect.center
        if self.zoom_con[0] is not None and zoom < self.zoom_con[0] / self.zoom_offset:
            zoom = self.zoom_con[0] / self.zoom_offset
        if self.zoom_con[1] is not None and zoom > self.zoom_con[1] / self.zoom_offset:
            zoom = self.zoom_con[1] / self.zoom_offset
        premade = [e / zoom for e in self.i_size]
        if premade[0] > self._constraint.size[0] or premade[1] > self._constraint.size[1]:
            m_ind = min((0, 1), key=lambda e: self._constraint.size[e] - premade[e])
            self.set_zoom(self.i_size[m_ind] / self._constraint.size[m_ind] * self.zoom_offset)
            return
        self.rect.size = premade
        self.rect.center = center
        self.rect.clamp_ip(self._constraint)
        self._target_zoom = zoom

    def reload_zoom(self, old_offset=1):
        self.set_zoom(self.get_zoom() * old_offset)

    zoom = property(get_zoom, set_zoom)

    def get_current_zoom(self):
        """
        Масштабирование камеры в данный момент.
        :return: int
        """
        return self.i_size[0] / self.c_rect.width

    def get_center(self):
        """
        Целевая позиция камеры
        :return: (x, y)
        """
        return self.rect.center

    def set_center(self, pos):
        """
        Установка целевой позиции камеры.
        :param pos: (x, y)
        """
        self.rect.center = pos

    center = property(get_center, set_center)

    def get_constraint(self):
        return self._constraint

    def set_constraint(self, rect):
        self._constraint = pygame.Rect(rect)
        self.reload_zoom()

    constraint = property(get_constraint, set_constraint)

    def move_constraint(self, rect):
        self._constraint = pygame.Rect(rect)
        self.rect.clamp_ip(self._constraint)

    def get_size(self):
        return self.i_size

    def set_size(self, size):
        self.i_size = size
        self.reload_zoom()

    size = property(get_size, set_size)

    def instant_move(self):
        self.c_rect.center = self.rect.center

    def instant_zoom(self):
        self.c_rect.size = self.rect.size

    def instant_target(self):
        """
        Мнгновенно установить камеру в целевую позицию
        """
        self.c_rect = self.rect.copy()

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
    """
    Класс игрового мира.
    Имеет свой собственный GUI, независимый от Main.gui
    За миром закреплена 1 собственная камера. class Camera
    Максимум 1 группа объектов. (physics.ObjectGroup)
    1 Система событий. (EventSystem)
    """

    def __init__(self, main, size=None, screen=None, zoom_offset=1, zoom_constraint=None):
        self.main = main
        self.size = size if size is not None else [6000, 6000]
        self.screen = pygame.Rect(screen if screen is not None else [0, 0, 800, 600])
        self.update_rect = pygame.Rect(0, 0, *self.size)
        z_const = zoom_constraint if zoom_constraint else [None, 4]

        self.camera = Camera((0, 0), self.screen, self.get_world_rect(), z_const, zoom_offset=zoom_offset)
        self.visible = self.camera.get_rect()

        self.player = None
        self.step_time = 1
        self.space_time_coef = 1
        self.event_system = None
        self.phys_group = None
        self.gui = None
        self.pressed = []
        self.paused = False
        self.mouse_window_prev = Vec2d(0, 0)
        self.mouse_world_prev = Vec2d(0, 0)
        self.mouse_window = Vec2d(0, 0)
        self.mouse_world = Vec2d(0, 0)

    def pregenerate(self):
        """
        Переопределяемый.
        Вызывается классом Main для подготовки уровня к запуску (Создание игровых объектов и т.д)
        """
        pass

    def add_internal(self, sprite):
        sprite.add(self.phys_group)

    def add(self, sprite):
        """
        Добавление спрайта.
        """
        self.add_internal(sprite)

    def send_event(self, event):
        if self.gui is not None:
            self.gui.send_event(event)
        if self.event_system:
            self.event_system.send_event(event)
        if not event.ignore:
            if self.player:
                self.player.send_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.camera.zoom /= .75
                elif event.button == 5:
                    self.camera.zoom *= .75

    def pause(self):
        self.space_time_coef = 0
        self.paused = True

    def unpause(self):
        self.space_time_coef = 1
        self.paused = False

    def end_game(self):
        self.main.home()

    def set_screen(self, rect, offset=1):
        """
        Устанавливает прямоугольник отрисовки.
        :param rect:
        :param offset: Коэффициент масштабирования
        """
        rect = pygame.Rect(rect)
        self.screen = rect
        self.camera.zoom_offset = offset
        self.camera.size = rect.size
        self.camera.reload_zoom(offset)
        self.camera.instant_target()
        self.update_group_draw()

    def update_group_draw(self):
        """
        Обновляет позиции отрисовки объектов и интерфейса вследствие изменения прямоугольника экрана.
        """
        if self.phys_group is not None:
            self.phys_group.draw_offset = self.screen.topleft
        if self.gui is not None:
            self.gui.rect = (0, 0, 100, 100)
            self.gui.absolute = False

    def world_to_local(self, pos):
        """
        Конвертирует координаты уровня в координаты камеры.
        См. Camera.world_to_local
        :param pos: (x, y)
        :return: Vec2d(x, y)
        """
        return self.camera.world_to_local(pos) + self.screen.topleft

    def local_to_world(self, pos):
        """
        Конвертирует координаты камеры в координаты уровня.
        См. Camera.local_to_world
        :param pos: (x, y)
        :return: Vec2d(x, y)
        """
        return self.camera.local_to_world([pos[n] - self.screen.topleft[n] for n in range(2)])

    def handle_keys(self):
        pressed = self.pressed
        if self.player is not None and not self.paused:
            self.player.handle_keys()

    def start_step(self, upd_time, time_coef=1):
        if not self.paused:
            self.step_time = upd_time * time_coef
            self.pressed = pygame.key.get_pressed()
            self.mouse_window_prev = self.mouse_window
            self.mouse_world_prev = self.mouse_world
            self.mouse_window = Vec2d(pygame.mouse.get_pos())
            self.mouse_world = self.calculate_mouse_world()
            if self.event_system:
                self.event_system.start_step(upd_time)
            if self.player is not None:
                tp = self.mouse_window - self.screen.center
                self.camera.center = self.player.position + tp
        if self.gui is not None:
            self.gui.start_step(upd_time)

    def end_step(self):
        if self.gui is not None:
            self.gui.end_step()

    def update(self):
        if not self.paused:
            self.camera.update(self.step_time)
            self.visible = self.camera.get_rect()
            if self.event_system:
                self.event_system.update()
            if self.phys_group is not None:
                self.phys_group.update(self.step_time * self.space_time_coef)
        if self.gui is not None:
            self.gui.update()

    def draw(self, surface):
        if self.phys_group is not None:
            self.phys_group.draw(surface, self.camera)
        if self.gui is not None:
            self.gui.draw(surface)

    def get_world_rect(self):
        """
        Возвращает прямоугольник, описывающий границы уровня.
        :return: Rect(topleft=(0, 0))
        """
        return pygame.Rect(0, 0, *self.size)

    def calculate_mouse_world(self):
        """
        Не рекомендуется к использованию - функция перерасчёта.
        Её результат записывается в Level.mouse_world
        :return: Vec2d(x, y)
        """
        ms = pygame.mouse.get_pos()
        sc, vs = self.screen.size, self.visible.size
        zoom = max((sc[0] / vs[0], sc[1] / vs[1]))
        return (Vec2d(ms) - self.screen.topleft) / zoom + self.visible.topleft


class Event:
    """
    Никак не связано с pygame.event.
    Прикрепляется к уровню,
    также как и все объекты имеет start_step, update_ end_step, но с фиксированным временем между итерациями.
    """

    def __init__(self, es=None):
        """
        :param es: class EventSystem - если указано, событие само добавляется в список системы событий.
        """
        self.event_system = es
        if es:
            self._level = self.event_system.level
            es.add(self)
        else:
            self._level = None

        self.step_time = 1

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level

    def start_step(self, upd_time):
        self.step_time = upd_time

    def update(self):
        """
        Переопределяемый.
        Вызывается каждый игровой тик.
        """
        pass

    def active_update(self):
        """
        Переопределяемый.
        Вызывается через фиксированное время.
        """
        pass

    def act(self):
        """
        Переопределяемый.
        Действия события.
        По-умолчанию не вызывается.
        """
        pass


class EventSystem:
    """
    Система событий уровня.
    Хранит список событий и вызывает их обновления.
    """

    def __init__(self, level):
        self._level = level
        self.events = []

        self.step_time = 1

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level
        for event in self.events:
            event.level = level

    def add(self, event):
        if event not in self.events:
            self.events.append(event)
            event.level = self._level

    def send_event(self, event):
        if event.type == EVENT.EVENT_SYSTEM:
            self.active_update()

    def start_step(self, upd_time):
        self.step_time = upd_time
        for i in self.events:
            i.start_step(upd_time)

    def update(self):
        for event in self.events:
            event.update()

    def active_update(self):
        for event in self.events:
            event.active_update()
