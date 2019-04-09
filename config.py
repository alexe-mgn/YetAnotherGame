SIZE_COEF = 1
MASS_COEF = 1
VISION_SIZE = (1200 * SIZE_COEF, 1200 * SIZE_COEF)
VIDEO_FIT = False


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
    UNLIVING = 5
    CREATURE = 10
    CREATURE_BOTTOM = CREATURE - 1
    CREATURE_TOP = CREATURE + 1
    COMPONENT = 15
    WEAPON = 15
    STATIC = 20
    PROJECTILE = 25


class COLLISION_TYPE(NS):
    TRACKED = 5
    PROJECTILE = 5
    SHIELD = 10


class ROLE:
    COMPONENT = 0
    ENGINE = 1
    WEAPON = 2


class TEAM:
    DEFAULT = 0
    PLAYER = 1
    ENEMY = 2
    NEUTRAL = 3
