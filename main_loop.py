import pygame
import sys
from main_settings import except_hook
from base_class import Level


sys.excepthook = except_hook


class Main:

    def __init__(self):
        self.size = [900, 600]
        self.winflag = pygame.RESIZABLE
        self.screen = pygame.display.set_mode(self.size, self.winflag)
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
        self.load_level(Level([6000, 6000], self.size))
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            self.update()

    def update(self):
        upd_time = self.clock.tick()
        if not 0 < upd_time < 10:
            upd_time = 1
        self.level.start_step()
        pressed = pygame.key.get_pressed()
        ms_pos = pygame.mouse.get_pos()
        self.level.send_keys(pressed)
        for event in pygame.event.get():
            self.level.send_event(event)
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.size = list(event.size)
                pygame.display.set_mode(self.size, self.winflag)

        self.level.update(upd_time)
        self.render()
        self.level.end_step()
        pygame.display.flip()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.level.draw(self.screen)


if __name__ == '__main__':
    main = Main()
    main.start()
