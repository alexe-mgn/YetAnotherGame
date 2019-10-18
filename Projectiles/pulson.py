from Engine.config import COLLISION_TYPE, CHANNEL
from Engine.geometry import Vec2d
from Engine.loading import load_model, cast_model, load_sound
from Engine.physics import BaseProjectile

import pymunk

NAME = __name__.split('.')[-1]
MODEL = load_model('Projectiles\\Models\\%s' % (NAME,))

CS = Vec2d(170, 170)


class Projectile(BaseProjectile):
    size_inc = 2.25
    hit_damage = 350
    damping = .5
    sound = {
        'explode': [load_sound('Projectiles\\Models\\flagdrop', ext='wav'), {'channel': CHANNEL.PULSON_EXPLOSION}]
    }

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.density = 1
        self.shape.collision_type = COLLISION_TYPE.PROJECTILE
        self.explosion = False
        self._image.n = 1

    def damage(self, val):
        pass

    def effect(self, obj, arbiter, first=True):
        if self.explosion:
            cps = arbiter.contact_point_set
            if cps.points:
                pc_depth = abs(cps.points[0].distance) / self.shape.radius
                obj.body.apply_impulse_at_local_point(
                    (cps.normal * (10000000 * pc_depth * (1 if first else -1))),
                    (0, 0))
                obj.damage(self.hit_damage * pc_depth)

    def death(self):
        self.explode()

    def explode(self):
        self.play_sound('explode')
        self._image.n = 0
        self._image.fps = 20
        self._image.que_end(self.kill)
        self.explosion = True

    def update(self):
        if self.explosion:
            self.shape.unsafe_set_radius(self.R_LIST[self._image.n])

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)
        cls.precalculate_shape()
        cls.calculate_poly_shape()

    @classmethod
    def precalculate_shape(cls):
        radius = 12
        rs = (6, 7, 12, 18, 36, 58, 90, 120, 146)

        cls.RADIUS = radius * cls.size_inc
        cls.R_LIST = [e * cls.size_inc for e in rs]

    @classmethod
    def calculate_poly_shape(cls):
        img_poly_left = []
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Projectile.init_class()
