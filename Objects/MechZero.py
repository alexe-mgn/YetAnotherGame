import pymunk
from Engine.config import ROLE
from Engine.geometry import Vec2d
from Engine.loading import load_model, cast_model
from game_class import YTGBaseCreature
from Engine.physics import Mount

NAME = __name__.split('.')[-1]
MODEL = load_model('Objects\\Models\\%s' % (NAME,))

CS = Vec2d(42, 77)


class Creature(YTGBaseCreature):
    size_inc = 1
    max_health = 300

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.density = 1

        self.init_mounts((Mount(self, allowed=[ROLE.ENGINE], top=False), 'engine'),
                         (Mount(self, allowed=[ROLE.WEAPON], top=False,
                                position=self.image_to_local((43, 11))), 'weapon_left'),
                         (Mount(self, allowed=[ROLE.WEAPON], top=False,
                                position=self.image_to_local((43, 143))), 'weapon_right'))

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)
        cls.precalculate_shape()
        cls.calculate_poly_shape()

    @classmethod
    def precalculate_shape(cls):
        radius = 50

        cls.RADIUS = radius * cls.size_inc

    @classmethod
    def calculate_poly_shape(cls):
        img_poly_left = []
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Creature.init_class()
