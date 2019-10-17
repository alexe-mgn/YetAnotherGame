import sys
import os
import traceback
import time
from config import LOAD_RELATIVE, LOAD_MEIPASS, EXCEPTION_FILE
"""
File path handling, exception output, +
"""

cwd = os.getcwd()
PATH_RELATIVE = '.'
PATH_MEIPASS = getattr(sys, '_MEIPASS', '.')
PATH_FILE = os.path.dirname(os.path.abspath(__file__))
PATH = (PATH_RELATIVE if LOAD_RELATIVE else
        (PATH_MEIPASS
         if LOAD_MEIPASS and getattr(sys, 'frozen', False)
         else PATH_FILE)
        )
WRITE_PATH = cwd


# Получить правильный путь к файлу относительно папки игры
def get_path(path):
    return os.path.join(PATH, path)


# Если файл будет использоваться для вывода
def get_write_path(path):
    return os.path.join(WRITE_PATH, path)


# Вывод ошибок
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
