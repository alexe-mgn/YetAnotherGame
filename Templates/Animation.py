import pymunk
from geometry import Vec2d, FRect
from loading import load_frames, cast_frames
from physics import BaseAnimation
from config import *

NAME = ''
S_PATH = 'Animations\\Frames\\%s' % (NAME,)
FRAMES = load_frames(S_PATH)

FRAME_CENTER = [(0, 0)] * len(FRAMES)


class Animation(BaseAnimation):
    SIZE_INCS = [SIZE_COEF] * len(FRAMES)

    def __init__(self):
        super().__init__()

    @classmethod
    def init_class(cls):
        cls._image, cls.IMAGE_SHIFTS = cast_frames(FRAMES, FRAME_CENTER, cls.SIZE_INCS)
        cls.calculate_collision_shape()

    @classmethod
    def calculate_collision_shape(cls):
        pass


Animation.init_class()
