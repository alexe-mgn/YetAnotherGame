import pymunk
from geometry import Vec2d
from loading import load_model, cast_model
from game_class import BaseProjectile
from VFX.dissipation import VideoEffect
from config import *

NAME = __name__.split('.')[-1]
MODEL = load_model('Projectiles\\Models\\%s' % (NAME,))

CS = Vec2d(76.5, 28.5)


class Projectile(BaseProjectile):
    mat = MAT_TYPE.ENERGY
    size_inc = 1
    lifetime = 1500
    hit_damage = 10

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.density = 1
        self._image.fps = 10

    def damage(self, val):
        pass

    def effect(self, obj, arbiter, first=True):
        obj.damage(self.hit_damage)
        self.death()

    def death(self):
        v = VideoEffect()
        v.add(self.groups())
        v.pos = self.pos
        self.kill()

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)
        cls.precalculate_shape()
        cls.calculate_poly_shape()

    @classmethod
    def precalculate_shape(cls):
        radius = 9

        cls.RADIUS = radius * cls.size_inc

    @classmethod
    def calculate_poly_shape(cls):
        img_poly_left = []
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Projectile.init_class()
