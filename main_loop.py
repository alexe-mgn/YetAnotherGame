import pygame
import sys
import os
from main_settings import except_hook
from config import *
from loading import get_path, load_image

sys.excepthook = except_hook
pygame.init()
pygame.display.set_mode((300, 300))

# Need display initialized
from Game.GUI import MainMenu
from Game.Levels.Survival import Survival


class Main:

    def __init__(self):
        # pygame.init()
        self.winflag = pygame.RESIZABLE | pygame.DOUBLEBUF
        self.level, self.gui, self.clock, self.running = None, None, None, False
        self.size = [800, 600]
        pygame.display.set_caption(APP_NAME)
        if os.path.isfile(get_path('game_icon.ico')):
            pygame.display.set_icon(load_image('game_icon.ico'))

    def calculate_visible(self, c):
        tg = VISION_SIZE
        k = (max if VIDEO_FIT else min)([tg[n] / c[n] for n in range(2)])
        if VIDEO_FIT:
            visible = [tg[n] / k for n in range(2)]
            tl = (c[0] - visible[0]) // 2, (c[1] - visible[1]) // 2
            return k, pygame.Rect(*tl, *visible)
        else:
            return k, pygame.Rect(0, 0, *self.size)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self.screen = pygame.display.set_mode(size, self.winflag)
        self._size = self.screen.get_size()
        self.zoom_offset, self._visible = self.calculate_visible(self._size)
        if self.level is not None:
            self.level.set_screen(self._visible, self.zoom_offset)

    @property
    def rect(self):
        return pygame.Rect(self._visible)

    def load_level(self, level):
        self.level = level
        self.load_gui(None)
        if level is not None:
            self.level.set_screen(self._visible, self.zoom_offset)
        else:
            self.level = EmptyGameObject()
        self.level.pregenerate()

    def load_gui(self, gui):
        self.gui = gui
        if gui is not None:
            self.gui.main = self
        else:
            self.gui = EmptyGameObject()

    def start(self):
        t = EVENT_TIMER.dict()
        for k, v in EVENT.dict().items():
            pygame.time.set_timer(v, t[k])

        if self.gui is None:
            self.load_gui(EmptyGameObject())
        if self.level is None:
            self.home()
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            self.update()

    def update(self):
        upd_time = self.clock.tick(60)
        if not 0 < upd_time < 100:
            upd_time = 1
        self.screen.fill((0, 0, 0))
        gui = self.gui
        level = self.level
        gui.start_step(upd_time)
        level.start_step(upd_time)
        for event in pygame.event.get():
            event.ignore = False
            gui.send_event(event)
            level.send_event(event)
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.size = list(event.size)
            elif event.type == EVENT.FPS_COUNTER:
                pygame.display.set_caption(str(int(1000 / upd_time)))
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
        self.load_level(None)
        self.load_gui(MainMenu(main=self))

    def quit(self):
        self.running = False

    def load_survival(self):
        self.load_level(Survival(main=self))


if __name__ == '__main__':
    main = Main()
    main.start()
