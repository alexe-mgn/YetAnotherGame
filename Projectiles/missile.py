import pymunk
from geometry import Vec2d
from loading import load_model, cast_model
from game_class import BaseProjectile
from VFX.dissipation import VideoEffect
from config import *

NAME = __name__.split('.')[-1]
MODEL = load_model('Projectiles\\Models\\%s' % (NAME,))

CS = Vec2d(32, 12)


class Explosion(BaseProjectile):
    size_inc = .5
    mat = MAT_TYPE.ENERGY

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.density = 1
        self._image.fps = 10
        self._image.que_end(self.kill)

    def update(self):
        self.shape.unsafe_set_radius(self.R_LIST[self._image.n])

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(
            load_model('Projectiles\\Models\\explosion_frag'),
            None, cls.size_inc)
        cls.precalculate_shape()
        cls.calculate_poly_shape()

    @classmethod
    def precalculate_shape(cls):
        radius = 5
        rs = (30, 75, 85, 100, 125, 150, 175, 200, 225, 125, 125, 100, 50, 0, 0)

        cls.RADIUS = radius * cls.size_inc
        cls.R_LIST = [e * cls.size_inc for e in rs]

    @classmethod
    def calculate_poly_shape(cls):
        img_poly_left = []
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Explosion.init_class()


class Projectile(BaseProjectile):
    size_inc = 1
    damping = None
    health = 10
    lifetime = 2000
    hit_damage = 15

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.density = 1

        self.target = None
        self.boost = False

    def effect(self, obj, arbiter, first=True):
        obj.damage(self.hit_damage)
        self.death()

    def death(self):
        if not self.boost:
            super().death()
        else:
            v = Explosion()
            v.add(self.groups())
            v.pos = self.pos
            v.set_parent(self)
            self.kill()

    def update(self):
        if self.boost:
            self.body.apply_force_at_local_point((1000000, 0), (0, 0))

    def launch(self):
        self.boost = True
        self.damping = 0

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
        img_poly_left = [(0, 0), (71, 1)]
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Projectile.init_class()
