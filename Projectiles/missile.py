from VFX.smoked import VideoEffect

from Engine.config import MAT_TYPE, CHANNEL
from Engine.geometry import Vec2d, angular_distance
from Engine.loading import load_model, cast_model, load_sound
from Engine.physics import BaseProjectile

import pymunk

NAME = __name__.split('.')[-1]
MODEL = load_model('Projectiles\\Models\\%s' % (NAME,))

CS = Vec2d(107, 43)


class Explosion(BaseProjectile):
    hit_damage = 15
    size_inc = .4
    mat = MAT_TYPE.ENERGY

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.mass = 1000
        self._image.fps = 20
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
        rs = (30, 75, 85, 100, 125, 150, 175, 200, 225, 125, 125, 100, 50, 1, 1)

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
    damping = 0
    max_health = 10
    lifetime = 3000
    hit_damage = 15
    sound = {
        'launch': [load_sound('Projectiles\\Models\\mini_launch', ext='wav', volume=.5),
                   {'channel': CHANNEL.MINI_LAUNCH}]
    }
    death_effect = VideoEffect

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Poly(self.body, self.POLY_SHAPE)
        self.shape.density = 1

        self.target = None
        self.boost = False

    def effect(self, obj, arbiter, first=True):
        if self.boost:
            obj.damage(self.hit_damage)
            self.death()

    def death(self):
        if self.health > 0 and not self.boost:
            self.emit_death_effect()
        else:
            v = Explosion()
            v.add(*self.groups())
            v.position = self.position
            v.set_parent(self)
        self.kill()

    def update(self):
        if self.boost:
            self.body.apply_force_at_local_point((5000000, 0), (0, 0))
            if self.target is not None:
                if hasattr(self.target, '__call__'):
                    tp = self.target()
                else:
                    tp = list(self.target)
                da = angular_distance(self.angle, (Vec2d(tp) - self.position).angle)
                self.angle += da * .1

    def launch(self):
        self.play_sound('launch')
        self.boost = True
        self.damping = 0
        self._image.fps = 10

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)
        cls.precalculate_shape()
        cls.calculate_poly_shape()

    @classmethod
    def precalculate_shape(cls):
        radius = 15

        cls.RADIUS = radius * cls.size_inc

    @classmethod
    def calculate_poly_shape(cls):
        img_poly_left = [(75, 31), (146, 33)]
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Projectile.init_class()
