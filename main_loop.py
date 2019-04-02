import pygame
import sys
from main_settings import except_hook
from base_class import Level


sys.excepthook = except_hook
pygame.init()


class Main:

    def __init__(self):
        # pygame.init()
        self.winflag = pygame.RESIZABLE
        self.size = [900, 600]
        self.level, self.clock, self.running = None, None, False

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self.screen = pygame.display.set_mode(size, self.winflag)
        self._size = list(size)

    def load_level(self, level):
        self.level = level

    def start(self):
        pygame.time.set_timer(30, 250)

        if self.level is None:
            self.load_level(Level([6000, 6000], self.size))
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            self.update()

    def update(self):
        upd_time = self.clock.tick(240)
        if not 0 < upd_time < 100:
            upd_time = 1
        self.level.start_step(upd_time)
        for event in pygame.event.get():
            self.level.send_event(event)
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.size = list(event.size)
                pygame.display.set_mode(self.size, self.winflag)
            elif event.type == 30:
                pygame.display.set_caption(str(1000 / upd_time))
        self.level.handle_keys()
        self.level.update()
        self.level.end_step()
        self.render()
        pygame.display.flip()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.level.draw(self.screen)


if __name__ == '__main__':
    main = Main()
    main.start()
