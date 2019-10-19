import os
import sys
import traceback
import time
from Engine.utils import *

"""App settings"""

APP_NAME = r'PyMunk based physics engine'
CODE_APP_NAME = transform_name(APP_NAME)
EXCEPTION_FILE = '%s_traceback.txt' % (CODE_APP_NAME,)

LOAD_MEIPASS = True
LOAD_RELATIVE = False

WINDOW_SIZE = (800, 600)
VISION_SIZE = (1200, 1200)
VIDEO_FIT = False


class DEBUG(NameSpace):
    DRAW = False
    COLLISION = False


"""Routing"""


class PATH(NameSpace):
    EXECUTABLE = os.getcwd()
    RELATIVE = '.'
    MEIPASS = getattr(sys, '_MEIPASS', EXECUTABLE)
    ENGINE = os.path.dirname(os.path.abspath(__file__))
    WRITE = EXECUTABLE
    LOAD = RELATIVE if LOAD_RELATIVE else (MEIPASS if LOAD_MEIPASS and getattr(sys, 'frozen', False) else EXECUTABLE)


# Получить правильный путь к файлу относительно папки игры
def get_path(path):
    return os.path.join(PATH.LOAD, path)


def get_engine_path(path):
    return os.path.join(PATH.ENGINE)


# Если файл будет использоваться для вывода
def get_write_path(path):
    return os.path.join(PATH.WRITE, path)


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


def debug_print(v):
    print(v)


"""Events"""

MOUSE_EVENTS = (5, 6)
KEY_EVENTS = (2, 3)
CONTROL_EVENTS = (2, 3, 5, 6)


class EVENT(NameSpace):
    FPS_COUNTER = 29
    EVENT_SYSTEM = 30


class EVENT_TIMER(NameSpace):
    FPS_COUNTER = 250
    EVENT_SYSTEM = 500


class DRAW_LAYER(NameSpace):
    DEFAULT = 15
    UNLIVING = 5
    CREATURE = 10
    CREATURE_BOTTOM = CREATURE - 1
    CREATURE_TOP = CREATURE + 1
    COMPONENT = 15
    WEAPON = 15
    STATIC = 20
    PROJECTILE = 25
    VFX = 30


"""Sound"""

CAMERA_SOUND_HEIGHT = 300
SOUND_QUARTER_DISTANCE = 1000
SOUND_COEF = .25 * (SOUND_QUARTER_DISTANCE + 1)


# Reserved sound channels
class CHANNEL(NameSpace):
    pass


"""Physics"""


class COLLISION_TYPE(NameSpace):
    TRACKED = 5
    PROJECTILE = 6


# Material type for collisions
class MAT_TYPE(NameSpace):
    MATERIAL = 0
    ENERGY = 1


class ROLE(NameSpace):
    OBJECT = 0
    COMPONENT = 1
    ENGINE = 2
    WEAPON = 3
    PROJECTILE = 4
    CREATURE = 5


class TEAM(NameSpace):
    DEFAULT = 0
    PLAYER = 1
    ENEMY = 2
    NEUTRAL = 3
