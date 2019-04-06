SIZE_COEF = 1
MASS_COEF = 1


class NS:

    def __iter__(self):
        return [e for e in dir(self) if e not in self.builtins]

    @classmethod
    def init_class(cls):
        cls.builtins = dir(cls)


NS.init_class()


class DRAW_LAYER:
    PLANET = 0
    WEAPON = 5
    SHIP = 10
    SHIP_BOTTOM = SHIP - 1
    SHIP_TOP = SHIP + 1
    COMPONENT = 15
    ENGINE = 15
    PROJECTILE = 20
    FIELD = 30


class COLLISION_TYPE(NS):
    TRACKED = 5
    PROJECTILE = 5
    SHIELD = 10


class ROLE:
    COMPONENT = 0
    ENGINE = 1
    WEAPON = 2


class TEAM:
    PLAYER = 0
    ENEMY = 1