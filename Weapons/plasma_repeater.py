from game_class import YTGBaseWeapon

from Engine.config import CHANNEL
from Engine.geometry import Vec2d
from Engine.loading import load_model, cast_model, load_sound

import pymunk

NAME = __name__.split('.')[-1]
MODEL = load_model('Weapons\\Models\\%s' % (NAME,))

CS = Vec2d(13, 17)


class Weapon(YTGBaseWeapon):
    name = NAME
    max_health = 40
    size_inc = 1.25
    proj_velocity = 1200
    fire_delay = 100
    sound = {
        'fire': [load_sound('Weapons\\Models\\explosion_dull'), {'channel': CHANNEL.PLASMA_WEAPON}]
    }

    def __init__(self):
        super().__init__()

        self.i_body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS, self.image_to_local((26, 17)))
        self.shape.density = 1

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)
        cls.precalculate_shape()
        cls.calculate_poly_shape()
        from Projectiles.plasma_bolt import Projectile
        cls.Projectile = Projectile
        cls.fire_pos = cls.image_to_local((65, 17))

    @classmethod
    def precalculate_shape(cls):
        radius = 22

        cls.RADIUS = radius * cls.size_inc

    @classmethod
    def calculate_poly_shape(cls):
        img_poly_left = []
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Weapon.init_class()
