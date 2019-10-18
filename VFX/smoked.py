from Engine.geometry import Vec2d
from Engine.loading import load_model, cast_model, GObject
from Engine.physics import StaticImage

NAME = __name__.split('.')[1]
MODEL = load_model('VFX\\Models\\%s' % (NAME,))

CS = Vec2d(170, 170)


class VideoEffect(StaticImage):
    size_inc = .6

    def __init__(self):
        super().__init__()
        self._image = GObject(self._frames)
        self._image.fps = 10
        self._image.que_end(self.kill)
        size = self._image.get_size()
        a = (size[0] * size[0] + size[1] * size[1]) ** .5
        self.size = (a, a)

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)


VideoEffect.init_class()
