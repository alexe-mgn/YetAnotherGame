import pygame
from geometry import Vec2d
from main_settings import get_path
import os
from math import ceil


def load_image(path):
    surface = pygame.image.load(get_path(path)).convert_alpha()
    return surface


def cast_image(source, center, size_inc):
    i_size = Vec2d(source.get_size())
    size = ceil(i_size * size_inc)
    img_center = ceil(center * size_inc)
    h_size = size / 2
    inc_vector = abs(img_center - h_size)
    hf_size = h_size + inc_vector
    tl = ceil(hf_size - img_center)

    img = pygame.Surface(hf_size * 2).convert_alpha()
    img.fill((255, 255, 255, 0))
    img.blit(pygame.transform.scale(source, size),
             tl)
    return img, -img_center


def load_frames(path):
    frames = []
    f_path = get_path(path)
    for f in os.listdir(f_path):
        fp = os.path.join(f_path, f)
        if f.endswith('.png') and os.path.isfile(fp):
            frames.append(load_image(fp))
    return frames


def cast_frames(source, centers, size_incs):
    ln = len(source)
    i_sizes = [Vec2d(e.get_size()) for e in source]
    sizes = [ceil(i_sizes[n] * size_incs[n]) for n in range(ln)]
    mx = Vec2d(max(sizes, key=lambda e: e[0])[0], max(sizes, key=lambda e: e[1])[1])
    frames, shifts = [], []
    for n, f in enumerate(source):
        img = pygame.Surface(mx * 2).convert_alpha()
        img.fill((255, 255, 255, 0))
        center = ceil(Vec2d(centers[n] * size_incs[n]))
        tl = ceil(mx - center)
        img.blit(pygame.transform.scale(f, sizes[n]), tl)
        frames.append(img)
        shifts.append(-center)
    return frames, shifts


class GObject:

    def __init__(self, obj):
        try:
            frames = []
            for i in obj:
                frames.append(i)
            self._frames = frames
            self._len = len(frames)
            self._animated = True
        except TypeError:
            self._frames = [obj]
            self._len = 1
            self._animated = False
        self._size = self._frames[0].get_size()
        self.n = 0
        self._fps = 1
        self._ft = 1000 / self._fps
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

    def get_size(self):
        return self._size

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps):
        self._fps = fps
        self._ft = 1000 / fps

    @property
    def frame_time(self):
        return self._ft

    @frame_time.setter
    def frame_time(self, ft):
        self._ft = ft
        self._fps = 1000 / ft

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
