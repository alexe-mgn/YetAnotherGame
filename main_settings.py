import sys
import os
import traceback
import time

APP_NAME = 'Game'
EXCEPTION_FILE = 'Game_traceback.txt'
LOAD_MEIPASS = True
PATH = (sys._MEIPASS if LOAD_MEIPASS and getattr(sys, 'frozen', False) else os.path.split(__file__)[0])


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


# For one file .exe to work
def get_path(path):
    return os.path.join(PATH, path)