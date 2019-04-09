import pygame
import sys
from main_settings import except_hook
from interface import Level
from config import *


sys.excepthook = except_hook
pygame.init()


class Main:

    def __init__(self):
        # pygame.init()
        self.winflag = pygame.RESIZABLE | pygame.DOUBLEBUF
        self.level, self.clock, self.running = None, None, False
        self.size = [900, 600]

    def calculate_visible(self, c):
        tg = VISION_SIZE
        k = (max if VIDEO_FIT else min)([tg[n] / c[n] for n in range(2)])
        return k, [tg[n] / k for n in range(2)]

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self.screen = pygame.display.set_mode(size, self.winflag)
        self._size = list(self.screen.get_size())
        self.zoom_offset, self._visible = self.calculate_visible(self._size)
        if self.level:
            self.level.set_screen_size(self._visible, self.zoom_offset)

    @property
    def visible(self):
        return self._visible

    def load_level(self, level):
        self.level = level

    def start(self):
        pygame.time.set_timer(30, 250)

        if self.level is None:
            self.load_level(Level([1000, 1000], self.size))
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            self.update()

    def update(self):
        upd_time = self.clock.tick(120)
        if not 0 < upd_time < 100:
            upd_time = 1
        self.screen.fill((0, 0, 0))
        self.level.start_step(upd_time)
        for event in pygame.event.get():
            self.level.send_event(event)
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.size = list(event.size)
            elif event.type == 30:
                pygame.display.set_caption(str(1000 / upd_time))
        self.level.handle_keys()
        self.level.draw(self.screen)
        self.level.update()
        self.level.end_step()
        # self.level.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    main = Main()
    main.start()
