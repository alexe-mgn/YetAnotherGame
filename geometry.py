import pygame


class FRect:
    """
    Float precision version of pygame.Rect class
    [WIP]
    """

    def __init__(self, x=None, y=0, w=0, h=0):
        if isinstance(x, pygame.Rect):
            self.pygame = x
        elif isinstance(x, FRect):
            for i in range(4):
                self[i] = x[i]
        else:
            if x is None:
                x = 0
            self._x = x
            self._y = y
            self._w = w
            self._h = h

    def move_ip(self, x, y):
        self._x += x
        self._y += y

    def move(self, x, y):
        new = FRect(self)
        new.move_ip(x, y)
        return new

    def inflate_ip(self, w, h):
        center = self.center
        self._w += w
        self._h += h
        self.center = center

    def inflate(self, w, h):
        new = FRect(self)
        new.inflate_ip(w, h)

    def clamp_ip(self, rect):
        if self.x < rect[0]:
            self.x = rect[0]
        elif self.right > rect[0] + rect[2]:
            self.right = rect[0] + rect[2]
        if self.right > rect[0] + rect[2]:
            self.centerx = rect[0] + rect[2] / 2

        if self.y < rect[1]:
            self.y = rect[1]
        elif self.bottom > rect[1] + rect[3]:
            self.bottom = rect[1] + rect[3]
        if self.bottom > rect[1] + rect[3]:
            self.centery = rect[1] + rect[3] / 2

    def clamp(self, rect):
        new = FRect(self)
        new.clamp_ip(rect)
        return new

    def clip_ip(self, rect):
        if not (self.x <= rect[0] + rect[2] and self.right >= rect[0]):
            return FRect(0, 0, 0, 0)
        if not (self.y <= rect[1] + rect[3] and self.bottom >= rect[1]):
            return FRect(0, 0, 0, 0)

        if self.x < rect[0]:
            self._x = rect[0]
        if self.right > rect[0] + rect[2]:
            self._w -= self.x - rect[0] - rect[2]

        if self.y < rect[1]:
            self._y = rect[1]
        if self.bottom > rect[1] + rect[3]:
            self._h -= self.y - rect[1] - rect[3]

    def clip(self, rect):
        new = FRect(self)
        new.clip_ip(rect)

    def contains(self, rect):
        return rect[0] >= self.x and \
               rect[0] + rect[2] <= self.right and \
               rect[1] >= self.y and \
               rect[1] + rect[3] <= self.bottom

    def collidepoint(self, pos):
        return self.x <= pos[0] <= self.right and \
               self.y <= pos[1] <= self.bottom

    def colliderect(self, rect):
        return (rect[0] <= self.x <= rect[0] + rect[2] or
                rect[0] <= self.right <= rect[0] + rect[2]) and \
               (rect[1] <= self.x <= rect[1] + rect[3] or
                rect[1] <= self.right <= rect[1] + rect[3])

    def make_int(self):
        for n in range(4):
            self[n] = int(self[n])

    def round(self, digs):
        for n in range(4):
            self[n] = round(self[n], digs)

    def __getitem__(self, ind):
        return [self._x, self._y, self._w, self._h][ind]

    def __setitem__(self, ind, val):
        setattr(self, ['_x', '_y', '_w', '_h'][ind], val)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'FRect(%s, %s, %s, %s)' % (self._x, self._y, self._w, self._h)

    @property
    def size(self):
        return [self._w, self._h]

    @size.setter
    def size(self, size):
        self._w, self._h = size[0], size[1]

    def get_w(self):
        return self._w

    def set_w(self, w):
        self._w = w

    w = property(get_w, set_w)
    width = property(get_w, set_w)

    def get_h(self):
        return self._h

    def set_h(self, h):
        self._h = h

    h = property(get_h, set_h)
    height = property(get_h, set_h)

    @property
    def topleft(self):
        return [self._x, self._y]

    @topleft.setter
    def topleft(self, pos):
        self._x, self._y = pos[0], pos[1]

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x

    x = property(get_x, set_x)
    left = property(get_x, set_x)

    def get_y(self):
        return self._y

    def set_y(self, y):
        self._y = y

    y = property(get_y, set_y)
    top = property(get_y, set_y)

    @property
    def right(self):
        return self._x + self._w

    @right.setter
    def right(self, x):
        self._x = x - self._w

    @property
    def bottom(self):
        return self._y + self._h

    @bottom.setter
    def bottom(self, y):
        self._y = y - self._h

    @property
    def bottomright(self):
        return [self._x + self._w, self._y + self._h]

    @bottomright.setter
    def bottomright(self, pos):
        self._x, self._y = pos[0] - self._w, pos[1] - self._h

    @property
    def topright(self):
        return [self._x + self._w, self.y]

    @topright.setter
    def topright(self, pos):
        self._x, self._y = pos[0] - self._w, pos[1]

    @property
    def pygame(self):
        return pygame.Rect(self._x, self._y, self._w, self._h)

    @pygame.setter
    def pygame(self, rect):
        self._x, self._y, self._w, self._h = rect[0], rect[1], rect[2], rect[3]

    @property
    def center(self):
        return [self._x + self._w / 2, self._y + self._h / 2]

    @center.setter
    def center(self, pos):
        self._x, self._y = pos[0] - self._w / 2, pos[1] - self._h / 2

    @property
    def centerx(self):
        return self._x + self._w / 2

    @centerx.setter
    def centerx(self, x):
        self._x = x - self._w / 2

    @property
    def centery(self):
        return self._y + self._h / 2

    @centery.setter
    def centery(self, y):
        self._y = y - self._h / 2
