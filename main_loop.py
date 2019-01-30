import pygame
import traceback
import sys
import time
from base_class import Level


APP_NAME = 'Game'
EXCEPTION_FILE = 'Game_traceback.txt'


def except_hook(cls, exception, c_traceback):
    if not getattr(sys, 'frozen', False):
        sys.__excepthook__(cls, exception, traceback)
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
        self.size = [600, 600]
        self.screen = pygame.display.set_mode(self.size)

    def start(self):
        self.running = True
        while self.running:
            self.update()

    def update(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        self.render()
        pygame.display.flip()

    def render(self):
        self.screen.fill((0, 0, 0))


if __name__ == '__main__':
    main = Main()
    main.start()
