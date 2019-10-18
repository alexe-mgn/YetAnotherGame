import pymunk
from Engine.geometry import Vec2d
from Engine.loading import load_model, cast_model
from game_class import YTGDynamicObject

NAME = __name__.split('.')[-1]
MODEL = load_model('Objects\\Models\\%s' % (NAME,))

CS = Vec2d(47, 53)


class Object(YTGDynamicObject):
    size_inc = 1
    max_health = 120

    def __init__(self, level):
        super().__init__()

        self.body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.density = 1

        self.level = level
        if getattr(level, 'add', None) is not None:
            level.add(self)

    def effect(self, obj, arbiter, first=True):
        if obj is self.level.player and obj.health < obj.max_health:
            obj.health += .25 * obj.max_health
            if obj.health > obj.max_health:
                obj.health = obj.max_health
            self.death()

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)
        cls.precalculate_shape()

    @classmethod
    def precalculate_shape(cls):
        radius = 50

        cls.RADIUS = radius * cls.size_inc


Object.init_class()
