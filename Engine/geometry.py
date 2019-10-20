import pygame

import operator
import math


def between(p, a, b, eq=None):
    if a >= b:
        en = a
        st = b
    else:
        en = b
        st = a
    if eq is None:
        eq = [True, True]
    return (st <= p if eq[0] else st < p) and (p <= en if eq[1] else p < en)


# def proj_intersection(p1, p2):
#     if p2[0] <= p1[1]:
#         if p2[0] >= p1[0]:
#             if p2[1] <= p1[1]:
#                 return p2[0], p2[1]
#             else:
#                 return p2[0], p1[1]
#         elif p2[1] >= p1[0]:
#             if p2[1] <= p1[1]:
#                 return p2[1], p1[0]
#             else:
#                 return p1[1], p1[0]
#         else:
#             return None, None
#     else:
#         return None, None


def normalized_angle(ang):
    """
    Return equivalent of given ang, but inside [0, 360)
    """
    # if ang < 0:
    #     ang = 360 - abs(ang) % 360
    # if ang >= 360:
    #     ang %= 360
    if not 0 <= ang < 360:
        ang %= 360
    return ang


def angular_distance(a, b):
    d = b - a
    if not 0 <= d < 360:
        d %= 360
    if d > 180:
        d -= 360
    return d


class FRect:
    """
    Float precision version of pygame.Rect class
    [WIP]
    """

    def __init__(self, x=None, y=0, w=0, h=0):
        if hasattr(x, '__getitem__'):
            for n in range(4):
                self[n] = x[n]
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
        new = self.copy()
        new.move_ip(x, y)
        return new

    def inflate_ip(self, w, h):
        center = self.center
        self._w += w
        self._h += h
        self.center = center

    def inflate(self, w, h):
        new = self.copy()
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
        new = self.copy()
        new.clamp_ip(rect)
        return new

    def clip_ip(self, rect):
        if not (self.x <= rect[0] + rect[2] and self.right >= rect[0]):
            return self.__class__(0, 0, 0, 0)
        if not (self.y <= rect[1] + rect[3] and self.bottom >= rect[1]):
            return self.__class__(0, 0, 0, 0)

        if self.x < rect[0]:
            self._x = rect[0]
        if self.right > rect[0] + rect[2]:
            self._w -= self.x - rect[0] - rect[2]

        if self.y < rect[1]:
            self._y = rect[1]
        if self.bottom > rect[1] + rect[3]:
            self._h -= self.y - rect[1] - rect[3]

    def clip(self, rect):
        new = self.copy()
        new.clip_ip(rect)

    def fit_ip(self, rect):
        ks = [rect[2] / self._w, rect[3] / self._h]
        k = min(ks)
        self._w, self._h = self._w * k, self._h * k
        self.center = (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2)

    def fit(self, rect):
        new = self.copy()
        new.fit_ip(rect)
        return new

    def union_ip(self, rect):
        l = min(self._x, rect[0])
        t = min(self._y, rect[1])
        r = max(self._x + self._w, rect[0] + rect[2])
        b = max(self._y + self._h, rect[1] + rect[3])
        self._x, self._y = l, t
        self._w, self._h = r - l, b - t

    def union(self, rect):
        new = self.__class__()
        l = min(self._x, rect[0])
        t = min(self._y, rect[1])
        r = max(self._x + self._w, rect[0] + rect[2])
        b = max(self._y + self._h, rect[1] + rect[3])
        new._x, new._y = l, t
        new._w, new._h = r - l, b - t
        return new

    def unionall_ip(self, rects):
        seq = tuple(rects) + (self,)
        l = min(map(lambda e: e[0], seq))
        t = min(map(lambda e: e[1], seq))
        r = max(map(lambda e: e[0] + e[2], seq))
        b = max(map(lambda e: e[1] + e[3], seq))
        self._x, self._y = l, t
        self._w, self._h = r - l, b - t

    def unionall(self, rects):
        new = self.__class__()
        seq = tuple(rects) + (self,)
        l = min(map(lambda e: e[0], seq))
        t = min(map(lambda e: e[1], seq))
        r = max(map(lambda e: e[0] + e[2], seq))
        b = max(map(lambda e: e[1] + e[3], seq))
        new._x, new._y = l, t
        new._w, new._h = r - l, b - t
        return new

    def contains(self, rect):
        return rect[0] >= self.x and \
               rect[0] + rect[2] <= self.right and \
               rect[1] >= self.y and \
               rect[1] + rect[3] <= self.bottom

    def collidepoint(self, x, y):
        return self.x <= x <= self.right and \
               self.y <= y <= self.bottom

    def colliderect(self, rect):
        return rect[0] - self._w <= self._x <= rect[0] + rect[2] and rect[1] - self._h <= self._y <= rect[1] + rect[3]

    def make_int(self):
        for n in range(4):
            self[n] = int(self[n])

    def int(self):
        new = self.copy()
        new.make_int()

    def round(self, digs):
        for n in range(4):
            self[n] = round(self[n], digs)

    def copy(self):
        return self.__class__(self._x, self._y, self._w, self._h)

    def __getitem__(self, ind):
        return [self._x, self._y, self._w, self._h][ind]

    def __setitem__(self, ind, val):
        setattr(self, ['_x', '_y', '_w', '_h'][ind], val)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return '%s(%s, %s, %s, %s)' % (self.__class__.__name__, self._x, self._y, self._w, self._h)

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

    @property
    def bottomleft(self):
        return [self._x, self._y + self._h]

    @bottomleft.setter
    def bottomleft(self, pos):
        self._x, self._y = pos[0], pos[1] - self._h

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

    def centered(self, pos):
        new = self.copy()
        new.center = pos
        return new


# Extended version of
# http://www.pygame.org/wiki/2DVectorClass
class Vec2d:
    """
    2d vector class, supports vector and scalar operators,
    and also provides a bunch of high level functions
    """
    __slots__ = ['x', 'y']

    def __init__(self, x_or_pair, y=None):
        if y is None:
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
        return '%s(%s, %s)' % (self.__class__.__name__, self.x, self.y)

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
        if isinstance(other, self.__class__):
            return self.__class__(f(self.x, other.x),
                                  f(self.y, other.y))
        elif (hasattr(other, "__getitem__")):
            return self.__class__(f(self.x, other[0]),
                                  f(self.y, other[1]))
        else:
            return self.__class__(f(self.x, other),
                                  f(self.y, other))

    def _r_o2(self, other, f):
        "Any two-operator operation where the right operand is a Vec2d"
        if (hasattr(other, "__getitem__")):
            return self.__class__(f(other[0], self.x),
                                  f(other[1], self.y))
        else:
            return self.__class__(f(other, self.x),
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
        if isinstance(other, self.__class__):
            return self.__class__(self.x + other.x, self.y + other.y)
        elif hasattr(other, "__getitem__"):
            return self.__class__(self.x + other[0], self.y + other[1])
        else:
            return self.__class__(self.x + other, self.y + other)

    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, self.__class__):
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
        if isinstance(other, self.__class__):
            return self.__class__(self.x - other.x, self.y - other.y)
        elif (hasattr(other, "__getitem__")):
            return self.__class__(self.x - other[0], self.y - other[1])
        else:
            return self.__class__(self.x - other, self.y - other)

    def __rsub__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(other.x - self.x, other.y - self.y)
        if (hasattr(other, "__getitem__")):
            return self.__class__(other[0] - self.x, other[1] - self.y)
        else:
            return self.__class__(other - self.x, other - self.y)

    def __isub__(self, other):
        if isinstance(other, self.__class__):
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
        if isinstance(other, self.__class__):
            return self.__class__(self.x * other.x, self.y * other.y)
        if (hasattr(other, "__getitem__")):
            return self.__class__(self.x * other[0], self.y * other[1])
        else:
            return self.__class__(self.x * other, self.y * other)

    __rmul__ = __mul__

    def __imul__(self, other):
        if isinstance(other, self.__class__):
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
        return self.__class__(operator.neg(self.x), operator.neg(self.y))

    def __pos__(self):
        return self.__class__(operator.pos(self.x), operator.pos(self.y))

    def __abs__(self):
        return self.__class__(abs(self.x), abs(self.y))

    def __invert__(self):
        return self.__class__(-self.x, -self.y)

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

    def resized(self, ln):
        new = self.__class__(self)
        new.length = ln
        return new

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
        return self.__class__(x, y)

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
        return self.__class__(self)

    def normalize_return_length(self):
        length = self.length
        if length != 0:
            self.x /= length
            self.y /= length
        return length

    def perpendicular(self):
        return self.__class__(-self.y, self.x)

    def perpendicular_normal(self):
        length = self.length
        if length != 0:
            return self.__class__(-self.y / length, self.x / length)
        return self.__class__(self)

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
        other, to_self = self.__class__(other), self.__class__(to_self)
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
        Builds a vector from self to intersection point of infinite lines build on self and other.
        """
        other = self.__class__(other)
        to_other = self.__class__(to_other)
        proj = self.scalar_axis_projection(other.perpendicular(), -to_other)
        if proj[0] != proj[1]:
            proj2 = other.scalar_axis_projection(self.perpendicular(), to_other)
            to_inter = self * (proj[0] / (proj[0] - proj[1]))
            # to_inter2 = other * (proj2[0] / (proj2[0] - proj2[1]))
            return to_inter, between(0, proj[0], proj[1], [True, True]) and between(0, proj2[0], proj2[1], [True, True])
            # between(to_inter.x, 0, self.x, [True, True]) and between(to_inter.y, 0, self.y, [True, True])
        else:
            return None, False

    def scalar_intersection(self, other, to_other):
        return

    def interpolate_to(self, other, range):
        return self.__class__(self.x + (other[0] - self.x) * range, self.y + (other[1] - self.y) * range)

    def convert_to_basis(self, x_vector, y_vector):
        return self.__class__(self.dot(x_vector) / x_vector.get_length_sqrd(),
                              self.dot(y_vector) / y_vector.get_length_sqrd())

    def get_quarter(self):
        if self.y >= 0:
            return 1 if self.x >= 0 else 2
        else:
            return 4 if self.x >= 0 else 3

    def int(self):
        return self.__class__(int(self.x), int(self.y))

    def make_int(self):
        self.x, self.y = int(self.x), int(self.y)

    @classmethod
    def from_anglen(cls, ang=0, ln=1):
        rad = math.radians(ang)
        return cls(math.cos(rad) * ln, math.sin(rad) * ln)

    def __ceil__(self):
        return self.__class__(math.ceil(self.x), math.ceil(self.y))

    def __getstate__(self):
        return [self.x, self.y]

    def __setstate__(self, dct):
        self.x, self.y = dct


'''
class Polygon:
    """
    Polygon class with support of most common methods/algorithms.
    (Not tested with concave, would work only in some cases.
    Also some algorithms don't support concave at all)
    It's not so optimal, a few unfinished, and need a lot of work on it.
    © github.com/alexe-mgn, alexe-mgn@mail.ru
    """
    polys = []

    def __init__(self, points, user=False):
        """
        It's recommended to have polygon points sorted clockwise.
        """
        self._angle = 0
        if points is None:
            points = []
        if isinstance(points, Polygon):
            self._angle = points._angle
            points = points.points
        elif hasattr(points, 'topleft'):
            points = [points.topright, points.topleft, points.bottomleft, points.bottomright]
        self.points = [Vec2d(point) for point in points]
        if user:
            self.polys.append(self)

    @staticmethod
    def normalized_angle(ang):
        """
        Return equivalent of given ang, but inside [0, 360)
        """
        if ang < 0:
            ang = 360 - abs(ang) % 360
        if ang >= 360:
            ang %= 360
        return ang

    def copy(self):
        """
        Return same polygon as self is, without any reference links.
        """
        new = self.__class__([Vec2d(point) for point in self])
        new._angle = self._angle
        return new

    def sort(self, clockwise=True):
        """
        Sort polygon points by angle.
        (A few bad method - uses inverse trigonometry functions)
        """
        center = self.center
        self.points.sort(key=lambda p: self.normalized_angle((p - center).get_angle()),
                         reverse=clockwise)

    def sorted(self, clockwise=True):
        """
        Return sorted version of self.
        """
        new = self.copy()
        new.sort(clockwise)
        return new

    def convex(self):
        """
        Make possibly-concave polygon convex depending on outer points.
        """
        self.sort()
        marked = []
        for n, p in enumerate(self.get_points()):
            poly = self.copy()
            del poly[n]
            if p in poly:
                marked.append(n)
        for n in marked[::-1]:
            del self[n]

    def is_convex(self):
        """
        Check if polygon is convex.
        """
        for n, p in enumerate(self):
            poly = self.copy()
            del poly[n]
            if p in poly:
                return False
        return True

    def convexed(self):
        """
        Return convex version of self.
        """
        new = self.copy()
        new.convex()
        return new

    def move(self, shift):
        """
        Move polygon by shift vector.
        """
        for point in self.points:
            point += shift

    def moved(self, shift):
        """
        Shifted version of self.
        """
        new = self.copy()
        new.move(shift)
        return new

    def move_to(self, pos, point=None):
        """
        Move polygon such way, that point (default=center) would be in given pos.
        """
        if point is None:
            point = self.center
        self.move(Vec2d(pos) - point)

    def moved_to(self, pos, point=None):
        """
        Moved version of self
        """
        if point is None:
            point = self.center
        return self.moved(Vec2d(pos) - point)

    def rotate(self, ang, pos=None):
        """
        Rotate self around pos (default=center) by specified in degrees angle.
        """
        if pos is None:
            pos = self.center
        for n, p in enumerate(self):
            vec_to = p - pos
            vec_to.rotate(ang)
            self[n] = pos + vec_to
        self._angle += ang

    def rotated(self, ang, pos=None):
        """
        Return rotated version of self.
        """
        new = self.copy()
        new.rotate(ang, pos)
        return new

    def zoom(self, coef, pos=None):
        if pos is None:
            pos = self.center
        for n, p in enumerate(self):
            self[n] = pos + (p - pos) / coef

    def zoomed(self, coef, pos=None):
        new = self.copy()
        new.zoom(coef, pos)
        return new

    def get_points(self):
        """
        Return points of polygon (Without reference links)
        For direct access use Polygon.points list
        """
        return [Vec2d(point) for point in self.points]

    def set_points(self, points):
        if isinstance(points, Polygon):
            points = points.get_points()
        self.points = [Vec2d(point) for point in points]

    def point(self, ind):
        """
        Return linked Vec2d point of polygon.
        Changing it would change the polygon, it's better to use for read-only.
        For unbound vector use polygon[i]
        """
        return self.points[(1 if ind >= 0 else -1) * abs(ind) % (len(self))]

    def edge(self, ind):
        """
        Return vector of edge from point[ind] to point[ind + 1]
        """
        return self.point(ind + 1) - self.point(ind)

    def flip(self, by_vertical=True, by_horizontal=False):
        """
        Flip polygon by (vertical) (and) (horizontal) axis
        """
        center = self.center
        for n, p in enumerate(self):
            if by_vertical:
                self.points[n][0] = 2 * center[0] - p[0]
            if by_horizontal:
                self.points[n][1] = 2 * center[1] - p[1]

    def flipped(self, by_vertical=True, by_horizontal=False):
        new = self.copy()
        new.flip(by_vertical, by_horizontal)
        return new

    def clip(self, other):
        return
        points = []
        for n, p in enumerate(self):
            for n2, p2 in enumerate(other):
                i_vec, inter = self.edge(n).intersection(other.edge(n2), p2 - p)
                pygame.draw.line(screen, (255, 0, 0), p, p + i_vec, 2)
                if inter:
                    i_p = p + i_vec
                    if i_p not in points:
                        points.append(p + i_vec)
                    p2n = other[n2 + 1]
                    if p2n in self and p2n not in points:
                        points.append(p2n)
        if len(points) > 2:
            self.points = points
            return True
        else:
            return None

    def clipped(self, other):
        return
        new = self.__class__(other)
        for n, p in enumerate(self):
            cut = 0
            for n2, p2 in enumerate(new):
                i_vec, inter = self.edge(n).intersection(other.edge(n2), p2 - p)
                pygame.draw.line(screen, (255, 0, 0), p, p + i_vec, 2)
                if inter:
                    if cut % 2 == 0:
                        new[n2 + cut // 2] = p + i_vec
                    else:
                        new.points.insert(n2 + cut // 2 + 1, p + i_vec)
                    cut += 1
        if len(new) > 2:
            return new
        else:
            return None

    @property
    def center(self):
        x, y = 0, 0
        n = 1
        for n, p in enumerate(self, 1):
            x += p[0]
            y += p[1]
        return Vec2d(x / n, y / n)

    @center.setter
    def center(self, pos):
        shift = pos - self.center
        self.move(shift)

    def centered(self, pos):
        new = self.__class__(self)
        new.center = pos
        return new

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, ang):
        rot = ang - self.normalized_angle(self._angle)
        self.rotate(rot)

    def get_area(self):
        a = 0
        for n in range(len(self) - 1):
            a += self.points[n][0] * self.points[n + 1][1] - self.points[n][1] * self.points[n + 1][0]
        return a

    def bounding(self, return_pygame=False):
        """
        Return bounding rectangle of polygon.
        """
        def get_x(e):
            return e[0]

        def get_y(e):
            return e[1]

        left = min(self, key=get_x)[0]
        right = max(self, key=get_x)[0]
        top = max(self, key=get_y)[1]
        bottom = min(self, key=get_y)[1]
        # if center is not None:
        #     mdx = max([left, right], key=lambda e: abs(center[0] - e))
        #     left, right = center[0] - mdx, center[1] + mdx
        #     mdy = max([top, bottom], key=lambda e: abs(center[1] - e))
        #     top, bottom = center[1] + mdy, center[1] - mdy
        if return_pygame:
            return pygame.Rect(left, bottom, right - left, top - bottom)
        else:
            return [Vec2d(left, top), Vec2d(right, bottom)]

    def maximum_bounding(self, pos=None, return_pygame=False):
        """
        Build rectangle with center in pos.
        Any rotated version of self around pos argument would be inside it.
        """
        if pos is None:
            pos = self.center
        dis = (max(self, key=lambda p: (p - pos).get_length_sqrd()) - pos).length + 1
        if return_pygame:
            return pygame.Rect(pos[0] - dis, pos[1] - dis, 2 * dis, 2 * dis)
        else:
            return [Vec2d(pos[0] - dis, pos[1] - dis), Vec2d(pos[0] + dis, pos[1] + dis)]

    def contains(self, point, crossing=True):
        """
        Check if point is inside polygon.
        """
        if Vec2d(point) in self.points:
            return True
        else:
            if crossing:
                return abs(self.collide_point(point)) == 1
            else:
                return abs(self.winding(point)) == 1

    def collide_point(self, point):
        intersections = 0
        ln = len(self)
        x, y = point
        for n, p in enumerate(self):
            s_x, s_y = p
            e_x, e_y = self.point((n + 1) % ln)
            x_min, x_max = min(s_x, e_x), max(s_x, e_x)
            y_min, y_max = min(s_y, e_y), max(s_y, e_y)
            # on horizontal edge
            if (s_y == e_y) and (s_y == y) and x_min < x < x_max:
                return -1
            if (y > y_min) and (y <= y_max) and (x <= x_max) and (s_y != e_y):
                x_inters = (((y - s_y) * (e_x - s_x)) / (e_y - s_y)) + s_x
                # on polygon edge
                if x_inters == x:
                    return -1
                # intersects edge
                if s_x == e_x or x <= x_inters:
                    intersections += 1

        return intersections % 2

    def __contains__(self, point, crossing=True):
        return self.contains(point)

    def nearest_line(self, point):
        """
        Return edge index assuming that INFINITE LINE build on it would be the nearest to the point, distance
        """
        mx = [None, None]
        for n, p in enumerate(self):
            edge = self.edge(n)
            to_point = point - p
            proj_y = abs(to_point.scalar_projection(edge.perpendicular()))
            if mx[1] is None or proj_y < mx[1]:
                mx[0] = n
                mx[1] = proj_y
        return mx[0], mx[1]

    def nearest_edge(self, point):
        """
        Return index of edge, that is the nearest to the given point, distance
        """
        mx = [None, None]
        for n, p in enumerate(self):
            edge = self.edge(n)
            to_point = point - p
            proj = to_point.scalar_projection(edge)
            if 0 <= proj <= edge.length:
                proj_y = abs(to_point.scalar_projection(edge.perpendicular()))
                if mx[1] is None or proj_y < mx[1]:
                    mx[0] = n
                    mx[1] = proj_y
        return mx[0], mx[1]

    def nearest_vertex(self, point):
        """
        Return index of vertex, that is the nearest to the given point, distance from vertex to point
        """
        mx = [None, None]
        for n, p in enumerate(self):
            ln = (point - p).get_length_sqrd()
            if mx[1] is None or ln < mx[1]:
                mx[0] = n
                mx[1] = ln
        return [mx[0], math.sqrt(mx[1])]

    def nearest_point(self, point):
        """
        Return point on perimeter of polygon, that is the nearest to the given one.

        Return
            - point
            - distance
            - vertex/edge index
            - bool(is vertex)
        """
        mx = [None, None, None]
        get_edge = self.edge
        for n, p in enumerate(self):
            edge = get_edge(n)
            to_point = point - p
            e_ln = edge.length
            if 0 < to_point.dot(edge) < e_ln**2:
                proj_y = abs(to_point.dot(edge.perpendicular()) / e_ln)
                if mx[1] is None or proj_y < mx[1]:
                    mx[0] = n
                    mx[1] = proj_y
                    mx[2] = False
            else:
                ln = to_point.length
                if mx[1] is None or ln < mx[1]:
                    mx[0] = n
                    mx[1] = ln
                    mx[2] = True
        if mx[2]:
            return self[mx[0]], mx[1], mx[0], mx[2]
        elif mx[2] is not None:
            p = self.points[mx[0]]
            to_point = point - p
            return p + to_point.projection(get_edge(mx[0])), mx[1], mx[0], mx[2]

    def minkowski(self, other):
        """
        UNSORTED AND UNFILTERED Minkowski addiction.
        Call convex() after sorting clockwise for resulting Minkowski polygon.
        """
        points = []
        for p1 in self:
            for p2 in other:
                points.append(p1 + p2)
        return self.__class__(points)

    def __add__(self, other):
        """
        Polygon is a set of points
        When we sum set of points we get minkowski addiction
        Return minkowski addiction of two polygons
        """
        return self.minkowski(other)

    def winding(self, wp):
        """
        Winding number of polygon around point.
        """
        w = 0
        for n in range(len(self)):
            p = n - 1
            v_in, v_out = self.edge(p), self.edge(n)
            if v_out[1] == 0:
                continue
            while v_in[1] == 0:
                p -= 1
                v_in = self.edge(p)
            vert_angle = (v_in[1] >= 0) == (v_out[1] <= 0)
            if self.hor_raycast_edge(n, wp, include_start=not vert_angle, include_end=False):
                w += (1 if v_out[1] > 0 else -1)
        return w

    def hor_raycast_edge(self, edge_ind, point, track_border=True, include_start=True, include_end=True):
        """
        Check if horizontal ray from point intersects edge.
        """
        vec = self.edge(edge_ind)
        p = self.point(edge_ind)
        if vec[1] == 0:
            return False
        if not include_start and p[1] == point[1]:
            return False
        if not include_end and (p + vec)[1] == point[1]:
            return False
        to_point = point - p

        proj_to_y_inter = between(to_point[1], 0, vec[1], [track_border] * 2)

        # Warning: Projection of vector is created counter-clockwise!
        normal = vec.perpendicular()
        proj = (-1 if to_point.dot(normal) >= 0 else 1)
        # proj_vec = to_point.projection(normal)
        # proj = (-1 if proj_vec.get_quarter() == normal.get_quarter() else 1)
        neg = proj <= 0 if track_border else proj < 0
        pos = proj >= 0 if track_border else proj > 0
        proj_to_vec_inter = (neg and 0 < vec[1]) or (vec[1] < 0 and pos)
        return proj_to_y_inter and proj_to_vec_inter

    def horizontal_intersection_num(self, point):
        """
        How much edges horizontal ray build from point would intersect.
        In other words, count crossing number of point and polygon.
        """
        c = 0
        hor_raycast_edge = self.hor_raycast_edge
        get_edge = self.edge
        edges = [get_edge(n) for n in range(len(self))]
        for n in range(len(self)):
            p = n - 1
            v_in, v_out = edges[p], edges[n]
            if v_out[1] == 0:
                continue
            while v_in[1] == 0:
                p -= 1
                v_in = edges[p]
            vert_angle = (v_in[1] >= 0) == (v_out[1] <= 0)
            if hor_raycast_edge(n, point, include_start=not vert_angle, include_end=False):
                c += 1
        return c

    def scalar_axis_projection(self, other, to_other):
        """
        Projection of polygon onto vector
        Return
           - Start x
           - End x
           - Start polygon vertex
           - End polygon vertex
        """
        mn, mx = [None, None], [None, None]
        for n, p in enumerate(self):
            proj = (p - to_other).scalar_projection(other)
            if mn[1] is None or proj < mn[1]:
                mn[0] = n
                mn[1] = proj
            if mx[1] is None or proj > mx[1]:
                mx[0] = n
                mx[1] = proj
        return mn[1], mx[1], mn[0], mn[1]

    def collide(self, other):
        """
        Check if two polygons intersect.
        (Uses Gilbert-Johnson-Keerthi algorithm)
        """
        other = self.__class__(other)
        cso = self.minkowski(-other)
        cso.convex()
        return [0, 0] in cso

    def collision_data(self, other):
        """
        Return
           - distance/depth
           - bool(objects intersect)
           - penetration vector
        """
        if isinstance(other, Circle):
            data = self.nearest_point(other.center)
            if not data[3]:
                vec = self.edge(data[2]).perpendicular()
            else:
                vec = other.center - self[data[2]]
            if self.contains(other.center):
                inter = True
                dis = data[1] + other.r
            else:
                inter = data[1] < other.r
                dis = other.r - data[1]
            vec.length = dis
            return abs(dis), inter, vec, data[0]  # other.pos - vec * ((other.r / dis) - 1)
        else:
            return self.GJK(other)

    def GJK(self, other):
        """
        Call Gilbert-Johnson-Keerthi algorithm and return distance/penetration depth of two polygons,
        check if two polygons intersect and compute vector, by which other should be moved to stop/start intersecting

        Return
           - distance/depth (length of penetration vector)
           - bool(polygons intersect)
           - penetration vector
           - collision point on polygon's perimeter
        """
        # other = self.__class__(other)
        # cso = self.minkowski(-other)
        # cso.convex()
        # data = cso.nearest_point([0, 0])
        # ip = self.nearest_point(data[0] + other.center)[0]
        # pygame.draw.circle(screen, (255, 0, 0), ip.int(), 4)
        # return data[1], [0, 0] in cso, data[0]

        other = self.__class__(other)
        points = []
        origin = {}
        for n1, p1 in enumerate(self):
            for n2, p2 in enumerate(-other):
                p = p1 + p2
                points.append(p)
                origin[id(p)] = n1
        cso = self.__class__(None)
        cso.points = points
        cso.convex()

        data = cso.nearest_point([0, 0])

        o1, o2 = origin[id(cso.point(data[2]))], origin[id(cso.point(data[2] + 1))]
        if data[3] or o1 == o2:
            ip = self.points[o1]
        else:
            ip = self.points[o1] + (data[0] - cso.points[data[2]])

        return data[1], [0, 0] in cso, data[0], ip

    def SAT(self, other):
        """
        Compute intersection using Separating axis theorem.
        """
        other = self.__class__(other)
        p_data = [None, None, None, None]
        for pi, poly, poly2 in ((0, self, other), (1, other, self)):
            for n, p in enumerate(poly):
                axis = poly.edge(n).perpendicular()
                ps = self.scalar_axis_projection(axis, p)
                po = other.scalar_axis_projection(axis, p)
                st, end = proj_intersection(ps, po)
                pygame.draw.line(screen, (100, 100, 100), p, p + axis)
                pygame.draw.line(screen, (0, 255, 0), p + axis.resized(ps[0]), p + axis.resized(ps[1]), 2)
                pygame.draw.line(screen, (255, 0, 0), p + axis.resized(po[0]), p + axis.resized(po[1]))
                if st is None:
                    return None, False, None
                if p_data[1] is None or abs(end - st) < abs(p_data[1]):
                    p_data[0] = n
                    p_data[1] = end - st
                    p_data[2] = axis
                    p_data[3] = pi
        p_data[2].length = p_data[1]
        return abs(p_data[1]), True, p_data[2]

    def __getitem__(self, ind):
        return Vec2d(self.points[(1 if ind >= 0 else -1) * abs(ind) % (len(self))])

    def __setitem__(self, ind, value):
        self.points[(1 if ind >= 0 else -1) * abs(ind) % (len(self))] = Vec2d(value)

    def __delitem__(self, ind):
        del self.points[ind]

    def __iter__(self):
        return iter(self.points)

    def __neg__(self):
        return self.__class__([-point for point in self])

    def __len__(self):
        return len(self.points)

    def __repr__(self):
        return '{1}({0})'.format('; '.join('[{0}, {1}]'.format(*point) for point in self), self.__class__.__name__)

    def draw(self, surface, color=(255, 0, 0), width=1):
        """
        Draw polygon onto pygame.Surface
        """
        pygame.draw.polygon(surface, color, [list(point) for point in self.points], width)


class Circle:

    def __init__(self, pos, r=None):
        if r is None:
            if hasattr(pos, 'topleft'):
                r = min(pos.size) / 2
                pos = pos.center
            else:
                poly = Polygon(pos)
                pos = poly.center
                r = (max(poly, key=lambda p: (p - pos).get_length_sqrd()) - pos).length
        self._p = Vec2d(*pos)
        self.r = r

    def copy(self):
        return Circle(self._p, self.r)

    def move(self, shift):
        self._p += shift

    def moved(self, shift):
        new = self.copy()
        new.move(shift)
        return new

    def get_pos(self):
        return self._p

    def set_pos(self, pos):
        self._p = Vec2d(pos)
    pos = property(get_pos, set_pos)
    center = property(get_pos, set_pos)

    def centered(self, pos):
        return Circle(pos, self.r)

    def rotate(self, ang):
        pass

    def rotated(self, ang):
        return self

    def bounding(self, return_pygame=False):
        if return_pygame:
            return pygame.Rect(self.center[0] - self.r, self.center[1] - self.r, self.r * 2, self.r * 2)
        else:
            return [Vec2d(self.center[0] - self.r, self.center[1] + self.r),
                    Vec2d(self.center[0] + self.r, self.center[1] - self.r)]

    def collision_data(self, other):
        """
        Return
           - distance/depth
           - bool(objects intersect)
           - penetration vector
        """
        if isinstance(other, Circle):
            t = self.r + other.r
            to_other = other.pos - self.pos
            dif = t - to_other.length
            to_other.length = dif
            return abs(dif), dif > 0, to_other, to_other * (self.r / abs(dif))
        else:
            data = Polygon(other).collision_data(self)
            return data[0], data[1], -data[2], data[3] - data[2]

    def draw(self, surface, color=(255, 0, 0), width=1):
        pygame.draw.circle(surface, color, [int(self.center[0]), int(self.center[1])], int(self.r), width)


test = 1
if __name__ != '__main__':
    test = None
if test == 1:
    from random import randint
    pygame.init()

    size = [800, 800]
    font = pygame.font.SysFont(None, 50)

    screen_real = pygame.display.set_mode(size)
    screen = pygame.Surface(size)
    p1, p2 = Polygon([[0, 0], [0, 100], [90, 60]], user=True), Polygon([[0, 0], [0, 60], [-30, 30]])
    p1.move([100, 50])
    p2.move([100, 400])
    p2 = p1.rotated(90, p1.bounding(return_pygame=True).topleft)
    p2.move([-20, 0])
    msm = p1.minkowski(-p2)
    msm.convex()
    Polygon.polys.append(p2)
    Polygon.polys.append(msm)
    cols = [[randint(0, 4) * 63, randint(0, 4) * 63, randint(0, 4) * 63] for _ in Polygon.polys]
    ruler = None
    poly = None

    running = True
    flip = True
    while running:
        ms = [pygame.mouse.get_pos()[0], size[1] - pygame.mouse.get_pos()[1]] if flip else pygame.mouse.get_pos()
        pressed = pygame.key.get_pressed()
        mods = pygame.key.get_mods()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if poly is not None:
                        poly = None
                    else:
                        for p in Polygon.polys:
                            if ms in p:
                                poly = p
                                break
                elif event.button == 3:
                    print(msm.contains(ms))
                    print(msm.nearest_edge(ms))
                    print(p1.collide(p2))
                elif event.button == 4:
                    if poly is not None:
                        if mods & pygame.KMOD_SHIFT:
                            poly.zoom(.5)
                        else:
                            poly.rotate(10)
                elif event.button == 5:
                    if poly is not None:
                        if mods & pygame.KMOD_SHIFT:
                            poly.zoom(2)
                        else:
                            poly.rotate(-10)
                elif event.button == 2:
                    ruler = ms
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    ruler = None
        if poly is not None:
            poly.move_to(ms)
            msm.set_points(p1.minkowski(-p2).convexed())
        if pressed[pygame.K_k]:
            msm.center = p1.center

        screen.fill((255, 255, 255))
        if ruler is not None:
            pygame.draw.line(screen, (255, 0, 0), ruler, ms, 1)
            screen.blit(
                pygame.transform.flip(
                    font.render(
                        str((Vec2d(ms) - ruler).length),
                        1,
                        (255, 0, 0)),
                    False,
                    flip),
                [0, 0])

        p2.draw(screen)
        c = Circle(p2)
        inter = p2.collision_data(p1)
        if inter[1] or pressed[pygame.K_z]:
            p2.move(-inter[2])
            c.move(-inter[2])
        c.draw(screen)
        pygame.draw.circle(screen, (255, 0, 0), p2.center.int(), 6)
        pygame.draw.line(screen, (255, 0, 0), p2.center.int(), (p2.center - inter[2]).int(), 1)
        for n, p in enumerate(Polygon.polys):
            p.draw(screen, cols[n])
        pygame.draw.circle(screen, (255, 0, 0), inter[3].int(), 4)
        # for n in range(len(msm)):
        #     axis = msm.edge(n).perpendicular()
        #     pygame.draw.line(screen, (64, 64, 64), msm[n], msm[n] + axis)
        #     data = msm.scalar_axis_projection(axis, msm[n])
        #     axis.length = data[0]
        #     v2 = Vec2d(axis)
        #     v2.length = data[1]
        #     pygame.draw.line(screen, (0, 0, 255), msm[n] + axis, msm[n] + v2)
        #     pygame.draw.circle(screen, (0, 0, 255), (msm[n] + axis).int(), 2)
        np = msm.nearest_point(ms)[0]
        # pygame.draw.circle(screen, (255, 0, 0), [int(e) for e in np], 5)
        screen_real.blit(pygame.transform.flip(screen, False, flip), (0, 0))

        pygame.display.flip()

    pygame.quit()
elif test == 2:
    pygame.init()

    size = [800, 800]

    screen_real = pygame.display.set_mode(size)
    screen = pygame.Surface(size)
    c1, c2 = Vec2d(300, 300), Vec2d(300, 300)
    v1, v2 = Vec2d(200, -50), Vec2d(25, -100)

    running = True
    c = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if c is not None:
                        c = None
                    else:
                        if (c1 - event.pos).get_length_sqrd() <= (c2 - event.pos).get_length_sqrd():
                            c = [c1, v1]
                        else:
                            c = [c2, v2]
                elif event.button == 5:
                    if c is not None:
                        c[1].rotate(2)
                elif event.button == 4:
                    if c is not None:
                        c[1].rotate(-2)
        ms = pygame.mouse.get_pos()
        if c is not None:
            c[0][0], c[0][1] = ms[0], ms[1]
        to_2 = c2 - c1
        cd = c2
        d = v2.intersection(v1, -to_2)
        print(d[1])

        screen.fill((255, 255, 255))
        pygame.draw.line(screen, (255, 0, 0), c1, c1 + v1, 2)
        pygame.draw.line(screen, (0, 0, 255), c2, c2 + v2, 2)
        pygame.draw.line(screen, (0, 0, 0), c1, c1 + to_2, 2)
        pygame.draw.line(screen, (0, 255, 0), cd, cd + d[0], 2)
        screen_real.blit(pygame.transform.flip(screen, False, False), (0, 0))

        pygame.display.flip()

    pygame.quit()
'''
