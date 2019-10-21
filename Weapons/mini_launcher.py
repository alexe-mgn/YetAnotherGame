from game_class import YTGBaseWeapon
from Projectiles.missile import Projectile as Missile

from Engine.config import COLLISION_TYPE
from Engine.geometry import Vec2d
from Engine.loading import load_model, cast_model

import pymunk

NAME = __name__.split('.')[-1]
MODEL = load_model('Weapons\\Models\\%s' % (NAME,))

CS = Vec2d(14, 30)


class Projectile(Missile):

    def post_update(self):
        if not self.boost and self.age > 500 and self.alive():
            self.launch()


class Weapon(YTGBaseWeapon):
    name = NAME
    max_health = 40
    size_inc = 1
    proj_velocity = 250
    inaccuracy = .3
    fire_delay = 333
    # sound = {
    #     'fire': [load_sound('Weapons\\Models\\explosion_dull'), {'channel': CHANNEL.PLASMA_WEAPON}]
    # }

    def __init__(self):
        super().__init__()

        self.i_body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS, self.image_to_local((33, 30)))
        self.shape.density = 1
        self.shape.collision_type = COLLISION_TYPE.TRACKED

        self.fire_n = 0

    def spawn(self, cls):
        obj = cls()
        obj.add(*self.groups())
        obj.position = self.local_to_world(self.fire_pos[self.fire_n])
        return obj

    def force_fire(self, **kwargs):
        self.play_sound('fire')
        ang = self.angle + (self.fire_n - 1) * self.inaccuracy * 180

        proj = self.spawn_proj()
        proj.velocity = Vec2d.from_anglen(ang, self.proj_velocity)
        proj.angle = self.angle
        proj.target = kwargs.get('target_function', kwargs.get('target', None))

        self.fire_n = (self.fire_n + 1) % 3

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)
        cls.precalculate_shape()
        cls.calculate_poly_shape()
        cls.Projectile = Projectile
        cls.fire_pos = [
            cls.image_to_local((46, 20)),
            cls.image_to_local((31, 30)),
            cls.image_to_local((46, 40))
        ]
        # cls.fire_pos = cls.image_to_local((31, 30))

    @classmethod
    def precalculate_shape(cls):
        radius = 30

        cls.RADIUS = radius * cls.size_inc

    @classmethod
    def calculate_poly_shape(cls):
        img_poly_left = []
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Weapon.init_class()
