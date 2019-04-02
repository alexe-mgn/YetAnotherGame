import pygame
import pymunk
from geometry import Vec2d, FRect
from loading import load_image, cast_image
from game_class import BaseShip
from math import ceil

I_IMG = load_image('Ships\\Models\\Vessel.png')
I_SIZE = Vec2d(I_IMG.get_size())

I_IMG_CENTER = Vec2d(300, 395)


class Ship(BaseShip):
    SIZE_INC = 1 / 6

    def __init__(self):
        super().__init__()
        self._image = None
        del self._image
        size = self._image.get_size()
        a = (size[0] ** 2 + size[1] ** 2) ** .5
        self.rect = FRect(0, 0, 0, 0)
        self.rect.inflate_ip(a, a)

        self.body = pymunk.Body()
        self.shape = pymunk.Poly(self.body, self.COLLISION_SHAPE)
        self.shape.density = 1
        self.pos = [0, 0]

    @classmethod
    def init_class(cls):
        cls._image, cls.IMAGE_SHIFT = cast_image(I_IMG, I_IMG_CENTER, cls.SIZE_INC)
        cls.calculate_collision_shape()

    @classmethod
    def calculate_collision_shape(cls):
        img_poly_left = [(0, 395),
                         (0, 282),
                         (60, 35),
                         (256, -5),
                         (532, 18),
                         (720, 260)]
        # img_poly_left = [(0, 395),
        #                  (0, 282),
        #                  (12, 230),
        #                  (60, 150),
        #                  (140, 100),
        #                  (60, 95),
        #                  (55, 35),
        #                  (256, 0),
        #                  (580, 28),
        #                  (330, 190),
        #                  (720, 260)]
        poly_left = [tuple(e[n] - I_IMG_CENTER[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.COLLISION_SHAPE = [(e[0] * cls.SIZE_INC, e[1] * cls.SIZE_INC) for e in poly_left + poly_right]


Ship.init_class()
