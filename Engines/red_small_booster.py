import pymunk
from geometry import Vec2d, FRect
from loading import load_image, cast_image
from game_class import BaseEngine

NAME = 'red_small_booster'
I_IMG = load_image('Engines\\Models\\%s.png' % (NAME,))
I_SIZE = Vec2d(I_IMG.get_size())

I_IMG_CENTER = Vec2d(40, 19)


class Engine(BaseEngine):
    SIZE_INC = 1

    def __init__(self):
        super().__init__()
        self._image = None
        del self._image
        size = self._image.get_size()
        a = (size[0] ** 2 + size[1] ** 2) ** .5
        self.rect = FRect(0, 0, 0, 0)
        self.rect.inflate_ip(a, a)

        self.body = pymunk.Body()
        self._i_body = self.body
        self.shape = pymunk.Circle(self.body, self.RADIUS, self.image_to_local((30, 19)))
        self.shape.density = 1
        self.pos = [0, 0]

    @classmethod
    def init_class(cls):
        cls._image, cls.IMAGE_SHIFT = cast_image(I_IMG, I_IMG_CENTER, cls.SIZE_INC)
        cls.calculate_collision_shape()

    @classmethod
    def calculate_collision_shape(cls):
        radius = 22

        cls.RADIUS = radius * cls.SIZE_INC


Engine.init_class()
