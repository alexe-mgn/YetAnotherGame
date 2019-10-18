"""
Development variables
"""
APP_NAME = r'PyMunk based physics engine'
EXCEPTION_FILE = '%s_traceback.txt' % (APP_NAME,)
RECORDS_FILE = 'Game\\storage\\game_results.json'

LOAD_MEIPASS = True
LOAD_RELATIVE = True

VISION_SIZE = (1200, 1200)
VIDEO_FIT = False

CAMERA_SOUND_HEIGHT = 300
SOUND_QUARTER_DISTANCE = 1000
SOUND_COEF = .25 * (SOUND_QUARTER_DISTANCE + 1)

MOUSE_EVENTS = (5, 6)
KEY_EVENTS = (2, 3)
CONTROL_EVENTS = (2, 3, 5, 6)


class NS:
    """Simple namespace for subclassing"""

    @classmethod
    def values(cls):
        return [v for k, v in cls.__dict__.items() if k not in cls.builtins]

    @classmethod
    def dict(cls):
        return {k: v for k, v in cls.__dict__.items() if k not in cls.builtins}

    @classmethod
    def init_class(cls):
        cls.builtins = dir(cls)
        cls.builtins.append('builtins')


NS.init_class()


class EVENT(NS):
    FPS_COUNTER = 29
    EVENT_SYSTEM = 30


class EVENT_TIMER(NS):
    FPS_COUNTER = 250
    EVENT_SYSTEM = 500


class DRAW_LAYER:
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


# Reserved sound channels
class CHANNEL(NS):
    PLASMA_WEAPON = 0
    PULSON_WEAPON = 1
    PULSON_EXPLOSION = 2
    NET_WEAPON = 3
    MINI_LAUNCH = 4


class COLLISION_TYPE(NS):
    TRACKED = 5
    PROJECTILE = 6


# Material type for collisions
class MAT_TYPE:
    MATERIAL = 0
    ENERGY = 1


class ROLE:
    OBJECT = 0
    COMPONENT = 1
    ENGINE = 2
    WEAPON = 3
    PROJECTILE = 4
    CREATURE = 5


class TEAM(NS):
    DEFAULT = 0
    PLAYER = 1
    ENEMY = 2
    NEUTRAL = 3


class DEBUG:
    DRAW = False
    COLLISION = False


class EmptyGameObject:
    """
    Объект, который можно использовать при отсутствии GUI или уровня.
    """
    _draw_debug = False

    def start_step(self, upd_time):
        pass

    def update(self):
        pass

    def end_step(self):
        pass

    def send_event(self, event):
        pass

    def handle_keys(self):
        pass

    def draw(self, surface):
        pass

    def pregenerate(self):
        pass

    def set_screen(self, *args):
        pass

    @property
    def main(self):
        return

    @main.setter
    def main(self, o):
        pass

    def __bool__(self):
        return False
