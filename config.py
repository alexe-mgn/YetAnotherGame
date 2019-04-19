APP_NAME = r'Game'
EXCEPTION_FILE = '%s_traceback.txt' % (APP_NAME,)
LOAD_MEIPASS = True

VISION_SIZE = (1200, 1200)
VIDEO_FIT = False

MOUSE_EVENTS = (2, 3)
KEY_EVENTS = (5, 6)
CONTROL_EVENTS = (2, 3, 5, 6)


class NS:

    @classmethod
    def values(cls):
        dct = cls.__dict__
        return [v for k, v in dct.items() if k not in cls.builtins]

    @classmethod
    def init_class(cls):
        cls.builtins = dir(cls)
        cls.builtins.append('builtins')


NS.init_class()


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


class COLLISION_TYPE(NS):
    TRACKED = 5
    PROJECTILE = 5


class MAT_TYPE:
    MATERIAL = 0
    ENERGY = 1


class ROLE:
    OBJECT = 0
    COMPONENT = 1
    ENGINE = 2
    WEAPON = 3


class TEAM(NS):
    DEFAULT = 0
    PLAYER = 1
    ENEMY = 2
    NEUTRAL = 3


def collide_case(a, b):
    ta, tb = getattr(a, 'team', TEAM.DEFAULT), getattr(b, 'team', TEAM.DEFAULT)
    ma, mb = getattr(a, 'mat', MAT_TYPE.MATERIAL), getattr(b, 'mat', MAT_TYPE.MATERIAL)
    if ma == mb == MAT_TYPE.ENERGY:
        return False
    if ta != tb:
        return True
    elif ta == TEAM.DEFAULT:
        return True
    else:
        return False


class EmptyGameObject:
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
