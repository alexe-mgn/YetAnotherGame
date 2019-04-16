import pymunk
from geometry import Vec2d
from loading import load_model, cast_model
from game_class import BaseProjectile
from config import *

NAME = 'pulson'
MODEL = load_model('Projectiles\\Models\\%s' % (NAME,))

CS = Vec2d(170, 170)


class Projectile(BaseProjectile):
    size_inc = 2.5

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.density = 1
        self.damping = 0.005
        self.explosion = False

    def effect(self, obj, arbiter):
        if self.explosion:
            cps = arbiter.contact_point_set
            if cps.points:
                pc_depth = abs(cps.points[0].distance) / self.shape.radius
                obj.damage(200 * pc_depth)

    def on_life_end(self):
        self.explode()

    def explode(self):
        self._image.fps = 20
        self._image.que_end(self.kill)
        self.shape.density = 1000000
        self.explosion = True

    def update(self):
        if self.explosion:
            self.shape.unsafe_set_radius((self._image.n + 1) / 9 * self.MAX_RADIUS)

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)
        cls.precalculate_shape()
        cls.calculate_poly_shape()

    @classmethod
    def precalculate_shape(cls):
        radius = 9
        mr = 170

        cls.RADIUS = radius * cls.size_inc
        cls.MAX_RADIUS = mr * cls.size_inc

    @classmethod
    def calculate_poly_shape(cls):
        img_poly_left = []
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Projectile.init_class()
