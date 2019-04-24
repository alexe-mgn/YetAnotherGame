import sys
import os
import traceback
import time
from config import LOAD_RELATIVE, LOAD_MEIPASS, EXCEPTION_FILE
"""
File path handling, exception output, +
"""

cwd = os.getcwd()
PATH = ('.' if LOAD_RELATIVE else
        (getattr(sys, '_MEIPASS', '.')
         if LOAD_MEIPASS and getattr(sys, 'frozen', False)
         else os.path.dirname(os.path.abspath(__file__))))
WRITE_PATH = cwd


def get_path(path):
    return os.path.join(PATH, path)


def get_write_path(path):
    return os.path.join(WRITE_PATH, path)


def except_hook(cls, exception, c_traceback):
    if not getattr(sys, 'frozen', False):
        sys.__excepthook__(cls, exception, c_traceback)
    with open(get_write_path(EXCEPTION_FILE),
              mode='a') as error_file:
        error_file.write('\n' + time.asctime() + '\n')
        error_file.write(str(time.time()) + ' SSTE\n')
        error_file.write(str(cls) + '\n')
        error_file.write(str(exception) + '\n')
        error_file.write(''.join(traceback.format_tb(c_traceback)) + '\n')
