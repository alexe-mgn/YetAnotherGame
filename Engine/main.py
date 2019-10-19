from Engine.config import *
from Engine.loading import get_path, load_image
from Engine.utils import EmptyGameObject

import pygame

import sys

sys.excepthook = except_hook

pygame.init()
pygame.display.set_mode((300, 300))


# Need display to be initialized at this moment


class Main:
    """
    Приложение запускается с помощью экземпляра данного класса.
    Рекомендуется создать класс и определить в нём все необходимые методы.
    В первую очередь - self.home. С вызова этого метода по-сути начинается приложение.
    Обычно он загружает главное меню.
    Уровень и главный GUI задаются через set_level, set_gui.
    Учтите, что у class Level есть свой собственный GUI.
    """

    def __init__(self):
        self.winflag = pygame.RESIZABLE | pygame.DOUBLEBUF
        self.screen = None
        self._size = None
        self.zoom_offset = None
        self._visible = None
        self._gui, self._level, self.clock, self.running = None, None, None, False
        self.set_gui(None)
        self.set_level(None)
        self.set_screen_size(WINDOW_SIZE)
        pygame.display.set_caption(APP_NAME)
        if os.path.isfile(get_path('icon.ico')):
            pygame.display.set_icon(load_image('icon.ico'))

    def calculate_visible(self, window_size):
        """
        Рассчёт смещения коэффициента масштабирования и прямоугольника отображаемой области относителньо окна.
        :param window_size: (x, y)
        :return: int(zoom_offset), Rect()
        """
        tg = VISION_SIZE
        k = (max if VIDEO_FIT else min)([tg[n] / window_size[n] for n in range(2)])
        if VIDEO_FIT:
            visible = [tg[n] / k for n in range(2)]
            tl = (window_size[0] - visible[0]) // 2, (window_size[1] - visible[1]) // 2
            return k, pygame.Rect(*tl, *visible)
        else:
            return k, pygame.Rect(0, 0, *self.get_screen_size())
        # zoom_offset - world_dL / screen_dL
        # zoom - initial / current

    def get_screen_size(self):
        """
        :return: (x, y)
        """
        return self._size

    def set_screen_size(self, size):
        """
        :param size: (x, y)
        """
        self.screen = pygame.display.set_mode(size, self.winflag)
        self._size = self.screen.get_size()
        self.zoom_offset, self._visible = self.calculate_visible(self._size)
        if self._level is not None:
            self._level.set_screen(self._visible, self.zoom_offset)

    size = property(get_screen_size, set_screen_size)

    def get_visible_rect(self):
        """
        Прямоугольник в окне приложения, в котором происходит вся отрисовка.
        :return: Rect()
        """
        return pygame.Rect(self._visible)

    visible_rect = property(get_visible_rect)

    def get_level(self):
        return self._level

    def set_level(self, level):
        self._level = level
        # self.set_gui(None)
        if level is not None:
            level.main = self
            level.pregenerate()
            level.set_screen(self.get_visible_rect(), self.zoom_offset)
        else:
            self._level = EmptyGameObject()

    level = property(get_level, set_level)

    def get_gui(self):
        return self._gui

    def set_gui(self, gui):
        self._gui = gui
        if gui is not None:
            gui.main = self
        else:
            self._gui = EmptyGameObject()

    gui = property(get_gui, set_gui)

    def start(self):
        """
        Запуск основного цилка.
        """
        t = EVENT_TIMER.as_dict()
        # Создаём таймеры для игровых событий
        for k, v in EVENT.as_dict().items():
            pygame.time.set_timer(v, t[k])
        if not self._level:
            self.home()
        self.clock = pygame.time.Clock()
        self.running = True
        update = self.update
        while self.running:
            update()

    def update(self):
        """
        1 итерация.
        Состоит из следующих стадий.
        object.start_step(step time) - Подготовка к итерации
        object.send_event(event) - всем необходимым объектам отправляем информацию о произошедших собитиях по одному
        level.handle_keys() - позволяем уровню обработать нажатия клавишь
            (передаётся уровнем другим объектам по необходимости)
        object.update() - итерация
        object.end_step() - завершение итерации
        level/gui.draw(screen) - отрисовка объектами необходимой информации на экран
        """
        upd_time = self.clock.tick(60)
        # Почти не обновляем при больших задержках
        if not 0 < upd_time < 100:
            upd_time = 1
        self.screen.fill((0, 0, 0))
        gui = self._gui
        level = self._level

        gui.start_step(upd_time)
        level.start_step(upd_time)
        for event in pygame.event.get():
            event.ignore = False
            gui.send_event(event)
            level.send_event(event)
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Обновляем размеры окна
                self.size = list(event.size)
            elif event.type == EVENT.FPS_COUNTER:
                pygame.display.set_caption('{} - {} fps'.format(APP_NAME, str(int(1000 / upd_time))))
        level.handle_keys()
        # level.draw(self.screen)
        gui.update()
        level.update()

        gui.end_step()
        level.end_step()

        level.draw(self.screen)
        gui.draw(self.screen)
        pygame.display.flip()

    def home(self):
        """
        Выйти в главное меню. Ну или как захотите.
        """

    def quit(self):
        """
        Закрыть приложение.
        """
        self.running = False
