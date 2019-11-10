from Engine.geometry import Vec2d
from Engine.config import get_path
from Engine.config import DEBUG

import pygame

import os
from math import ceil


def load_sound(path, volume=1, ext='ogg'):
    fp = get_path(path + '.' + ext)
    s = pygame.mixer.Sound(fp)
    s.set_volume(volume)
    return s


def load_image(path, alpha=True):
    surface = pygame.image.load(get_path(path))
    return surface.convert_alpha() if alpha else surface.convert()


def cast_image(source, center=None, size_inc=1):
    """
    Обрезать по содержимому, центрировать и масштабировать изображение.
    :param source: pygame.Surface
    :param center: (x, y)
    :param size_inc: int
    :return: pygame.Surface, (x, y) - image shift
    """
    i_size = source.get_size()
    if center is None:
        center = [e / 2 for e in i_size]
    else:
        if center[0] is None:
            center[0] = i_size[0] / 2
        if center[1] is None:
            center[1] = i_size[1] / 2
    # Область, которую есть смысл отображать.
    b_rect = source.get_bounding_rect()
    # Её размер после масштабирования.
    b_size = ceil(Vec2d(b_rect.size) * size_inc)
    # Половина.
    h_size = b_size / 2
    # Центр обрезанного и масштабированного изображения относительно просто обрезанного.
    img_center = ceil((Vec2d(center) - b_rect.topleft) * size_inc)
    # Вектор масштабирования, вдоль которого растягивается новая поверхность,
    # чтобы центрированное изображение вместилось.
    inc_vector = abs(img_center - h_size)
    hf_size = h_size + inc_vector
    tl = hf_size - img_center

    bs = source.subsurface(b_rect)
    img = pygame.Surface(hf_size * 2).convert_alpha()
    img.fill((255, 255, 255, 0))
    img.blit(pygame.transform.scale(bs, b_size),
             tl)

    if DEBUG.DRAW:
        r = img.get_rect()
        r.w -= 2
        r.h -= 2
        pygame.draw.rect(img, (255, 0, 0), r, 2)
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
    """
    Обрезать по содержимому, центрировать и масштабировать кадры.
    :param source: pygame.Surface
    :param centers: [(x, y), ...]
    :param size_incs: [int, ...]
    :return: [pygame.Surface, ...], (x, y) - image shift
    """
    frames = []
    c0 = Vec2d(0, 0)
    for n, f in enumerate(source):
        i_size = f.get_size()
        center = centers[n]
        size_inc = size_incs[n]
        if center is None:
            center = [e / 2 for e in i_size]
        else:
            if center[0] is None:
                center[0] = i_size[0] / 2
            if center[1] is None:
                center[1] = i_size[1] / 2
        b_rect = f.get_bounding_rect()
        b_size = ceil(Vec2d(b_rect.size) * size_inc)
        h_size = b_size / 2
        img_center = ceil((Vec2d(center) - b_rect.topleft) * size_inc)
        if n == 0:
            c0 = -img_center
        inc_vector = abs(img_center - h_size)
        hf_size = h_size + inc_vector
        tl = hf_size - img_center

        bs = f.subsurface(b_rect)
        img = pygame.Surface(hf_size * 2).convert_alpha()
        img.fill((255, 255, 255, 0))
        img.blit(pygame.transform.scale(bs, b_size),
                 tl)
        if DEBUG.DRAW:
            r = img.get_rect()
            r.w -= 2
            r.h -= 2
            pygame.draw.rect(img, (255, 0, 0), r, 2)
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
        """
        Переопределяемый.
        """
        pass

    def que_start(self, func):
        """
        Выполняет функцию в начале каждого цикла анимации.
        """
        self.start_que.append(func)

    def start_cycle(self):
        for func in self.start_que:
            func()

    def que_end(self, func):
        """
        Выполняет функцию в конце каждого цикла анимации.
        """
        self.end_que.append(func)

    def end_cycle(self):
        for func in self.end_que:
            func()

    def read(self):
        return self._frames[self.n]

    image = property(read)

    def set_ind(self, n):
        self.n = n

    def __getitem__(self, ind):
        return self._frames[ind]

    def __repr__(self):
        return 'GObject([%s])' % (', '.join(str(e) for e in self._frames),)


def load_model(path):
    """
    Универсальная функция загрузки как для изображений, так и анимаций.
    :param path: str
    :return: pygame.Surface / [pygame.Surface, ...]
    """
    fp = get_path(path)
    if os.path.isfile(fp + '.png'):
        return load_image(path + '.png')
    elif os.path.isdir(fp):
        return load_frames(fp)


def cast_model(source, cs=None, sis=1):
    """
    Универсальная функция выравнивания.
    Преобразует аргументы и избирательно применяет cast_image / cast_image.
    :param source: pygame.Surface / [pygame.Surface, ...]
    :param cs: (x, y) / [(x, y), ...] - центр(ы)
    :param sis: int / [int, ...] - коэффициент(ы) масштабирования
    :return: pygame.Surface / [pygame.Surface, ...]
    """
    if not isinstance(source, pygame.Surface):
        ln = len(source)
        if cs is None or hasattr(cs[0], '__int__'):
            cs = [cs] * ln
        else:
            while len(cs) < ln:
                cs.append(None)
        if hasattr(sis, '__int__'):
            sis = [sis] * ln
        else:
            while len(sis) < ln:
                sis.append(sis[-1])
        return cast_frames(source, cs, sis)
    else:
        return cast_image(source, cs, sis)
