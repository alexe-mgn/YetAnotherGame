import pygame
import operator
import math


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


# Extended version of
# http://www.pygame.org/wiki/2DVectorClass
class Vec2d(object):
    """2d vector class, supports vector and scalar operators,
       and also provides a bunch of high level functions
       """
    __slots__ = ['x', 'y']

    def __init__(self, x_or_pair, y=None):
        if y == None:
            self.x = x_or_pair[0]
            self.y = x_or_pair[1]
        else:
            self.x = x_or_pair
            self.y = y

    def __len__(self):
        return 2

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("Invalid subscript " + str(key) + " to Vec2d")

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError("Invalid subscript " + str(key) + " to Vec2d")

    # String representaion (for debugging)
    def __repr__(self):
        return 'Vec2d(%s, %s)' % (self.x, self.y)

    # Comparison
    def __eq__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        else:
            return False

    def __ne__(self, other):
        if hasattr(other, "__getitem__") and len(other) == 2:
            return self.x != other[0] or self.y != other[1]
        else:
            return True

    def __nonzero__(self):
        return bool(self.x or self.y)

    # Generic operator handlers
    def _o2(self, other, f):
        "Any two-operator operation where the left operand is a Vec2d"
        if isinstance(other, Vec2d):
            return Vec2d(f(self.x, other.x),
                         f(self.y, other.y))
        elif (hasattr(other, "__getitem__")):
            return Vec2d(f(self.x, other[0]),
                         f(self.y, other[1]))
        else:
            return Vec2d(f(self.x, other),
                         f(self.y, other))

    def _r_o2(self, other, f):
        "Any two-operator operation where the right operand is a Vec2d"
        if (hasattr(other, "__getitem__")):
            return Vec2d(f(other[0], self.x),
                         f(other[1], self.y))
        else:
            return Vec2d(f(other, self.x),
                         f(other, self.y))

    def _io(self, other, f):
        "inplace operator"
        if (hasattr(other, "__getitem__")):
            self.x = f(self.x, other[0])
            self.y = f(self.y, other[1])
        else:
            self.x = f(self.x, other)
            self.y = f(self.y, other)
        return self

    # Addition
    def __add__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self.x + other.x, self.y + other.y)
        elif hasattr(other, "__getitem__"):
            return Vec2d(self.x + other[0], self.y + other[1])
        else:
            return Vec2d(self.x + other, self.y + other)

    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vec2d):
            self.x += other.x
            self.y += other.y
        elif hasattr(other, "__getitem__"):
            self.x += other[0]
            self.y += other[1]
        else:
            self.x += other
            self.y += other
        return self

    # Subtraction
    def __sub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self.x - other.x, self.y - other.y)
        elif (hasattr(other, "__getitem__")):
            return Vec2d(self.x - other[0], self.y - other[1])
        else:
            return Vec2d(self.x - other, self.y - other)

    def __rsub__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(other.x - self.x, other.y - self.y)
        if (hasattr(other, "__getitem__")):
            return Vec2d(other[0] - self.x, other[1] - self.y)
        else:
            return Vec2d(other - self.x, other - self.y)

    def __isub__(self, other):
        if isinstance(other, Vec2d):
            self.x -= other.x
            self.y -= other.y
        elif (hasattr(other, "__getitem__")):
            self.x -= other[0]
            self.y -= other[1]
        else:
            self.x -= other
            self.y -= other
        return self

    # Multiplication
    def __mul__(self, other):
        if isinstance(other, Vec2d):
            return Vec2d(self.x * other.x, self.y * other.y)
        if (hasattr(other, "__getitem__")):
            return Vec2d(self.x * other[0], self.y * other[1])
        else:
            return Vec2d(self.x * other, self.y * other)

    __rmul__ = __mul__

    def __imul__(self, other):
        if isinstance(other, Vec2d):
            self.x *= other.x
            self.y *= other.y
        elif (hasattr(other, "__getitem__")):
            self.x *= other[0]
            self.y *= other[1]
        else:
            self.x *= other
            self.y *= other
        return self

    # Division
    def __div__(self, other):
        return self._o2(other, operator.div)

    def __rdiv__(self, other):
        return self._r_o2(other, operator.div)

    def __idiv__(self, other):
        return self._io(other, operator.div)

    def __floordiv__(self, other):
        return self._o2(other, operator.floordiv)

    def __rfloordiv__(self, other):
        return self._r_o2(other, operator.floordiv)

    def __ifloordiv__(self, other):
        return self._io(other, operator.floordiv)

    def __truediv__(self, other):
        return self._o2(other, operator.truediv)

    def __rtruediv__(self, other):
        return self._r_o2(other, operator.truediv)

    def __itruediv__(self, other):
        return self._io(other, operator.floordiv)

    # Modulo
    def __mod__(self, other):
        return self._o2(other, operator.mod)

    def __rmod__(self, other):
        return self._r_o2(other, operator.mod)

    def __divmod__(self, other):
        return self._o2(other, operator.divmod)

    def __rdivmod__(self, other):
        return self._r_o2(other, operator.divmod)

    # Exponentation
    def __pow__(self, other):
        return self._o2(other, operator.pow)

    def __rpow__(self, other):
        return self._r_o2(other, operator.pow)

    # Bitwise operators
    def __lshift__(self, other):
        return self._o2(other, operator.lshift)

    def __rlshift__(self, other):
        return self._r_o2(other, operator.lshift)

    def __rshift__(self, other):
        return self._o2(other, operator.rshift)

    def __rrshift__(self, other):
        return self._r_o2(other, operator.rshift)

    def __and__(self, other):
        return self._o2(other, operator.and_)

    __rand__ = __and__

    def __or__(self, other):
        return self._o2(other, operator.or_)

    __ror__ = __or__

    def __xor__(self, other):
        return self._o2(other, operator.xor)

    __rxor__ = __xor__

    # Unary operations
    def __neg__(self):
        return Vec2d(operator.neg(self.x), operator.neg(self.y))

    def __pos__(self):
        return Vec2d(operator.pos(self.x), operator.pos(self.y))

    def __abs__(self):
        return Vec2d(abs(self.x), abs(self.y))

    def __invert__(self):
        return Vec2d(-self.x, -self.y)

    # vectory functions
    def get_length_sqrd(self):
        return self.x ** 2 + self.y ** 2

    def get_length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __setlength(self, value):
        length = self.get_length()
        self.x *= value / length
        self.y *= value / length

    length = property(get_length, __setlength, None, "gets or sets the magnitude of the vector")

    def rotate(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        self.x = x
        self.y = y

    def rotated(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        return Vec2d(x, y)

    def get_angle(self):
        if (self.get_length_sqrd() == 0):
            return 0
        return math.degrees(math.atan2(self.y, self.x))

    def __setangle(self, angle_degrees):
        self.x = self.length
        self.y = 0
        self.rotate(angle_degrees)

    angle = property(get_angle, __setangle, None, "gets or sets the angle of a vector")

    def get_angle_between(self, other):
        cross = self.x * other[1] - self.y * other[0]
        dot = self.x * other[0] + self.y * other[1]
        return math.degrees(math.atan2(cross, dot))

    def normalized(self):
        length = self.length
        if length != 0:
            return self / length
        return Vec2d(self)

    def normalize_return_length(self):
        length = self.length
        if length != 0:
            self.x /= length
            self.y /= length
        return length

    def perpendicular(self):
        return Vec2d(-self.y, self.x)

    def perpendicular_normal(self):
        length = self.length
        if length != 0:
            return Vec2d(-self.y / length, self.x / length)
        return Vec2d(self)

    def dot(self, other):
        return float(self.x * other[0] + self.y * other[1])

    def get_distance(self, other):
        return math.sqrt((self.x - other[0]) ** 2 + (self.y - other[1]) ** 2)

    def get_dist_sqrd(self, other):
        return (self.x - other[0]) ** 2 + (self.y - other[1]) ** 2

    def projection(self, other):
        other_length_sqrd = other[0] * other[0] + other[1] * other[1]
        projected_length_times_other_length = self.dot(other)
        return other * (projected_length_times_other_length / other_length_sqrd)

    def scalar_projection(self, other):
        return self.dot(other) / math.sqrt(other[0] ** 2 + other[1] ** 2)

    def axis_projection(self, other, to_self):
        """
        Calculates projection vector of self to other
        Returns start pos of projection and projection vector
        """
        other, to_self = Vec2d(other), Vec2d(to_self)
        return [to_self.projection(other), self.projection(other)]

    def scalar_axis_projection(self, other, to_self):
        """
        Return start and end cords of self projected on axis
        when to_self represents self start cords in this axis's plane
        """
        ln2 = math.sqrt(other[0] ** 2 + other[1] ** 2)
        st = (other[0] * to_self[0] + other[1] * to_self[1]) / ln2
        return [st, st + self.dot(other) / ln2]

    def cross(self, other):
        return self.x * other[1] - self.y * other[0]

    def intersection(self, other, to_other):
        """
        Builds a vector from self to intersection point of infinite lines build on self and other
        """
        other = Vec2d(other)
        to_other = Vec2d(to_other)
        proj = self.scalar_axis_projection(other.perpendicular(), -to_other)
        return self * (proj[0] / abs(proj[1] - proj[0]))

    def scalar_intersection(self, other, to_other):
        other = Vec2d(other)
        to_other = Vec2d(to_other)
        proj = self.scalar_axis_projection(other.perpendicular(), -to_other)
        return self * (proj[0] / abs(proj[1] - proj[0]))

    def interpolate_to(self, other, range):
        return Vec2d(self.x + (other[0] - self.x) * range, self.y + (other[1] - self.y) * range)

    def convert_to_basis(self, x_vector, y_vector):
        return Vec2d(self.dot(x_vector) / x_vector.get_length_sqrd(), self.dot(y_vector) / y_vector.get_length_sqrd())

    def get_quarter(self):
        if self.y >= 0:
            return 1 if self.x >= 0 else 2
        else:
            return 4 if self.x >= 0 else 3

    def __getstate__(self):
        return [self.x, self.y]

    def __setstate__(self, dct):
        self.x, self.y = dct