import pymunk
from geometry import Vec2d, FRect
from loading import load_image, cast_image, GObject
from game_class import BaseWeapon
from config import *

NAME = 'Pulson'
I_IMG = load_image('Weapons\\Models\\%s.png' % (NAME,))
I_SIZE = Vec2d(I_IMG.get_size())

I_IMG_CENTER = Vec2d(24, 30)


class Weapon(BaseWeapon):
    SIZE_INC = 2 * SIZE_COEF

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self._i_body = self.body
        self.shape = pymunk.Circle(self.body, self.RADIUS, offset=self.image_to_local((48, 30)))
        self.shape.density = MASS_COEF

    @classmethod
    def init_class(cls):
        cls._image, cls.IMAGE_SHIFT = cast_image(I_IMG, I_IMG_CENTER, cls.SIZE_INC)
        cls._image = GObject(cls._image)
        cls.calculate_collision_shape()

    @classmethod
    def calculate_collision_shape(cls):
        radius = 40

        cls.RADIUS = radius * cls.SIZE_INC


Weapon.init_class()
