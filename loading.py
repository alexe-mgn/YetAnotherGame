import pygame
from geometry import Vec2d
from main_settings import get_path
import os
from math import ceil


def load_image(path, alpha=True):
    surface = pygame.image.load(get_path(path))
    return surface.convert_alpha() if alpha else surface.convert()


def cast_image(source, center, size_inc):
    i_size = Vec2d(source.get_size())
    if center is None:
        center = i_size / 2
    else:
        if center[0] is None:
            center[0] = i_size[0] / 2
        if center[1] is None:
            center[1] = i_size[1] / 2
    size = ceil(i_size * size_inc)
    h_size = size / 2
    img_center = ceil(Vec2d(center) * size_inc if center is not None else h_size)
    inc_vector = abs(img_center - h_size)
    hf_size = h_size + inc_vector
    tl = ceil(hf_size - img_center)

    img = pygame.Surface(hf_size * 2).convert_alpha()
    img.fill((255, 255, 255, 0))
    img.blit(pygame.transform.scale(source, size),
             tl)
    # pygame.draw.rect(img, (255, 0, 0), img.get_rect(), 2)
    return img, -img_center


def load_frames(path):
    frames = []
    f_path = get_path(path)
    for f in os.listdir(f_path):
        fp = os.path.join(f_path, f)
        if f.endswith('.png') and os.path.isfile(fp):
            frames.append(load_image(fp))
    return frames


# def cast_frames(source, centers, size_incs):
#     frames = []
#     c0 = Vec2d(0, 0)
#     for n, f in enumerate(source):
#         b_rect = f.get_bounding_rect()
#         s_inc = size_incs[n]
#         b_size = Vec2d(b_rect.size) * s_inc
#         img = pygame.Surface(b_size).convert_alpha()
#         img.fill((255, 255, 255, 0))
#         c = Vec2d(centers[n] if centers[n] is not None else b_size / 2) * s_inc
#         tl = b_size / 2 - c
#         if n == 0:
#             c0 = c
#         img.blit(pygame.transform.scale(f,
#                                         [ceil(e * s_inc) for e in f.get_size()]),
#                  tl)
#         pygame.draw.rect(img, (255, 0, 0), img.get_rect(), 2)
#         frames.append(img)
#     return frames, c0

def cast_frames(source, centers, size_incs):
    frames = []
    c0 = Vec2d(0, 0)
    for n, f in enumerate(source):
        b_rect = f.get_bounding_rect()
        s_inc = size_incs[n]
        b_size = Vec2d(b_rect.size) * s_inc
        img = pygame.Surface(b_size).convert_alpha()
        img.fill((255, 255, 255, 0))
        c = Vec2d(centers[n] if centers[n] is not None else b_size / 2) * s_inc
        tl = b_size / 2 - c
        if n == 0:
            c0 = c
        img.blit(pygame.transform.scale(f,
                                        [ceil(e * s_inc) for e in f.get_size()]),
                 tl)
        # pygame.draw.rect(img, (255, 0, 0), img.get_rect(), 2)
        frames.append(img)
    return frames, c0


class GObject:

    def __init__(self, obj):
        if not isinstance(obj, pygame.Surface):
            frames = obj
            self._frames = frames[:]
            self._len = len(frames)
        else:
            self._frames = [obj]
            self._len = 1
        self._animated = False
        self._size = self._frames[0].get_size()
        self.n = 0
        self._fps = 0
        self._ft = 0
        self.cycles = 0
        self.last_upd = 0
        self.start_que = []
        self.end_que = []

    @property
    def frames(self):
        return self._frames

    @frames.setter
    def frames(self, frames):
        self._frames = frames
        self._len = len(frames)
        self._size = frames[0].get_size()

    def get_size(self):
        return self._size

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps):
        self._fps = fps
        if fps == 0:
            self._animated = False
            self._ft = 0
        else:
            self._animated = True
            self._ft = 1000 / fps

    @property
    def frame_time(self):
        return self._ft

    @frame_time.setter
    def frame_time(self, ft):
        self._ft = ft
        self._fps = 1000 / ft

    def on(self):
        self._animated = True

    def off(self):
        self._animated = False

    def update(self, upd_time):
        self.each_step()
        if self._animated:
            self.last_upd += upd_time
            if self.last_upd >= self._ft:
                if self.n == 0:
                    self.start_cycle()
                self.n += 1
                if self.n >= self._len:
                    self.end_cycle()
                    self.n = 0
                    self.cycles += 1
                self.last_upd -= self._ft

    def each_step(self):
        pass

    def que_start(self, func):
        self.start_que.append(func)

    def start_cycle(self):
        for func in self.start_que:
            func()

    def que_end(self, func):
        self.end_que.append(func)

    def end_cycle(self):
        for func in self.end_que:
            func()

    def read(self):
        return self._frames[self.n]

    image = property(read)

    def get_by_ind(self, n):
        return self._frames[n]

    def set_ind(self, n):
        self.n = n

    def __getitem__(self, ind):
        return self._frames[ind]

    def __repr__(self):
        return 'GObject([%s])' % (', '.join(str(e) for e in self._frames),)


def load_model(path):
    fp = get_path(path)
    if os.path.isfile(fp + '.png'):
        return load_image(path + '.png')
    elif os.path.isdir(fp):
        return load_frames(fp)


def cast_model(source, cs, sis):
    if not isinstance(source, pygame.Surface):
        ln = len(source)
        if cs is None or hasattr(cs[0], '__int__'):
            cs = [cs] * ln
        if hasattr(sis, '__int__'):
            sis = [sis] * ln
        return cast_frames(source, cs, sis)
    else:
        return cast_image(source, cs, sis)
