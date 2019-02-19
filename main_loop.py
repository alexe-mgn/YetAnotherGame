import pygame
import traceback
import sys
import time
from base_class import Level


APP_NAME = 'Game'
EXCEPTION_FILE = 'Game_traceback.txt'


def except_hook(cls, exception, c_traceback):
    if not getattr(sys, 'frozen', False):
        sys.__excepthook__(cls, exception, c_traceback)
    with open(EXCEPTION_FILE,
              mode='a') as error_file:
        error_file.write('\n' + time.asctime() + '\n')
        error_file.write(str(time.time()) + 'SSTE\n')
        error_file.write(str(cls) + '\n')
        error_file.write(str(exception) + '\n')
        error_file.write(''.join(traceback.format_tb(c_traceback)) + '\n')


sys.excepthook = except_hook


# For one file .exe to work
def get_file_path(path):
    if getattr(sys, 'frozen', False):
        return '\\'.join([sys._MEIPASS, path])
    else:
        return path


class Main:

    def __init__(self):
        self.size = [900, 600]
        self.winflag = pygame.RESIZABLE
        self.screen = pygame.display.set_mode(self.size, self.winflag)

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
        pressed = pygame.key.get_pressed()
        ms_pos = pygame.mouse.get_pos()
        self.level.send_keys(pressed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.size = list(event.size)
                pygame.display.set_mode(self.size, self.winflag)
            self.level.send_event(event)

        self.level.update(upd_time)
        self.render()
        pygame.display.flip()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.level.draw(self.screen)


if __name__ == '__main__':
    main = Main()
    main.start()
