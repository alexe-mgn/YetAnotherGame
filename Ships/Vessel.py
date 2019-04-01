import pygame
import pymunk
from geometry import Vec2d, FRect
from loading import load_image
from game_class import BaseShip
from math import ceil

I_IMG = load_image('Ships\\Models\\Vessel.png').convert_alpha()
I_SIZE = Vec2d(I_IMG.get_size())

I_IMG_CENTER = Vec2d(302, 395)


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
        cls.calculate_image()
        cls.calculate_collision_shape()

    @classmethod
    def calculate_image(cls):
        # size = [ceil(e * cls.SIZE_INC) for e in I_SIZE]
        # img_center = [(e * cls.SIZE_INC) for e in I_IMG_CENTER]
        # full_size = [ceil((e[0] - abs(e[1])) * 2 + 1) for e in zip(size, img_center)]
        #
        # img = pygame.Surface(full_size)
        # img.blit(pygame.transform.scale(I_IMG, size),
        #          [ceil(e[0] / 2 - e[1] - 1) for e in zip(full_size, img_center)])
        # cls._image = img
        size = ceil(I_SIZE * cls.SIZE_INC)
        img_center = I_IMG_CENTER * cls.SIZE_INC
        h_size = size / 2
        inc_vector = abs(img_center - h_size)
        hf_size = h_size + inc_vector
        tl = ceil(hf_size - img_center - 1)

        img = pygame.Surface(hf_size * 2)
        img.blit(pygame.transform.scale(I_IMG, size),
                 tl)
        cls._image = img
        cls.IMAGE_SHIFT = tl - hf_size

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
