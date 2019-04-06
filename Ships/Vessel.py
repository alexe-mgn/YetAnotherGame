import pymunk
from geometry import Vec2d, FRect
from loading import load_image, cast_image, GObject
from game_class import BaseShip, Mount
from config import *

NAME = 'Vessel'
I_IMG = load_image('Ships\\Models\\%s.png' % (NAME,))
I_SIZE = Vec2d(I_IMG.get_size())

I_IMG_CENTER = Vec2d(300, 395)


class Ship(BaseShip):
    SIZE_INC = 1 / 2 * SIZE_COEF

    def __init__(self):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Poly(self.body, self.COLLISION_SHAPE)
        self.shape.density = MASS_COEF
        self.init_mounts((Mount(self, position=self.image_to_local((80, 395)), allowed=(ROLE.ENGINE,)),
                          'middle_engine'),

                         (Mount(self, position=self.image_to_local((298, 240)), angle=105.36, allowed=(ROLE.ENGINE,
                                                                                                       ))),
                         (Mount(self, position=self.image_to_local((298, 550)), angle=-105.36,
                                allowed=(ROLE.ENGINE,))),

                         (Mount(self, position=self.image_to_local((630, 330)), angle=113.33,
                                allowed=(ROLE.ENGINE,))),
                         (Mount(self, position=self.image_to_local((630, 460)), angle=-113.33,
                                allowed=(ROLE.ENGINE,))),

                         (Mount(self, position=self.image_to_local((600, 395)), allowed=(ROLE.WEAPON,), top=False),
                          'main_weapon')
                         )

    @classmethod
    def init_class(cls):
        cls._image, cls.IMAGE_SHIFT = cast_image(I_IMG, I_IMG_CENTER, cls.SIZE_INC)
        cls._image = GObject(cls._image)
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
