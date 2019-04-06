import pymunk
from geometry import Vec2d, FRect
from loading import load_image, cast_image, GObject
from game_class import BaseShip, Mount
from config import *

NAME = ''
I_IMG = load_image('Ships\\Models\\%s.png' % (NAME,))
I_SIZE = Vec2d(I_IMG.get_size())

I_IMG_CENTER = Vec2d(0, 0)


class Ship(BaseShip):
    SIZE_INC = SIZE_COEF

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Poly(self.body, self.COLLISION_SHAPE)
        self.shape.density = MASS_COEF

    @classmethod
    def init_class(cls):
        cls._image, cls.IMAGE_SHIFT = cast_image(I_IMG, I_IMG_CENTER, cls.SIZE_INC)
        cls._image = GObject(cls._image)
        cls.calculate_collision_shape()

    @classmethod
    def calculate_collision_shape(cls):
        img_poly_left = []
        poly_left = [tuple(e[n] - I_IMG_CENTER[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.COLLISION_SHAPE = [(e[0] * cls.SIZE_INC, e[1] * cls.SIZE_INC) for e in poly_left + poly_right]


Ship.init_class()
