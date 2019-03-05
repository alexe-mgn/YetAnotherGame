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


class Polygon:
    """
    Polygon class with support of most common methods/algorithms.
    (Not tested with concave, would work only in some cases.
    Also some algorithms don't support concave at all)
    It's not so optimal, a few unfinished, and need a lot of work on it.
    © github.com/alexe-mgn, alexe-mgn@mail.ru
    """
    polys = []

    def __init__(self, *points, user=False):
        """
        It's recommended to have polygon points sorted clockwise.
        """
        first = points[0]
        self._angle = 0
        if isinstance(first, Polygon):
            self._angle = first._angle
            points = first.points
        elif hasattr(first, 'topleft'):
            points = [first.topright, first.topleft, first.bottomleft, first.bottomright]
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
        new = Polygon(*[Vec2d(point) for point in self])
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

    def shift(self, shift):
        """
        Move polygon by shift vector.
        """
        for point in self.points:
            point += shift

    def shifted(self, shift):
        """
        Shifted version of self.
        """
        new = self.copy()
        new.shift(shift)
        return new

    def move(self, pos, point=None):
        """
        Move polygon such way, that point (default=center) would be in given pos.
        """
        if point is None:
            point = self.center
        self.shift(Vec2d(pos) - point)

    def moved(self, pos, point=None):
        """
        Moved version of self
        """
        if point is None:
            point = self.center
        return self.shifted(Vec2d(pos) - point)

    def rotate(self, ang, pos=None):
        """
        Rotate self around pos (default=center) by specified in degrees angle.
        """
        if pos is None:
            pos = self.center
        for n, p in enumerate(self):
            vec_to = p - pos
            self[n] = pos + vec_to.rotated(ang)
        self._angle += ang

    def rotated(self, ang, pos=None):
        """
        Return rotated version of self.
        """
        new = self.copy()
        new.rotate(ang, pos)
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

    def edge(self, ind):
        """
        Return vector of edge from point[ind] to point[ind + 1]
        """
        return self[ind + 1] - self[ind]

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

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, ang):
        rot = ang - self.normalized_angle(self._angle)
        self.rotate(rot)

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
        dis = (max(self, key=lambda p: (p - pos).get_length_sqrd()) - pos).length
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
                return self.horizontal_intersection_num(point) % 2 == 1
            else:
                return abs(self.winding(point)) == 1

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
        for n, p in enumerate(self):
            edge = self.edge(n)
            to_point = point - p
            proj = to_point.scalar_projection(edge)
            if 0 < proj < edge.length:
                proj_y = abs(to_point.scalar_projection(edge.perpendicular()))
                if mx[1] is None or proj_y < mx[1]:
                    mx[0] = n
                    mx[1] = proj_y
                    mx[2] = False
            ln = (point - p).length
            if mx[1] is None or ln < mx[1]:
                mx[0] = n
                mx[1] = ln
                mx[2] = True
        if mx[2]:
            return self[mx[0]], mx[1], mx[0], mx[2]
        elif mx[2] is not None:
            p = self[mx[0]]
            to_point = point - p
            return p + to_point.projection(self.edge(mx[0])), mx[1], mx[0], mx[2]

    def minkowski(self, other):
        """
        UNSORTED AND UNFILTERED Minkowski addiction.
        Call convex() after sorting clockwise for resulting Minkowski polygon.
        """
        points = []
        for p1 in self:
            for p2 in other:
                points.append(Vec2d(p1 + p2))
        return Polygon(*points)

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
        p = self[edge_ind]
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
        for n in range(len(self)):
            p = n - 1
            v_in, v_out = self.edge(p), self.edge(n)
            if v_out[1] == 0:
                continue
            while v_in[1] == 0:
                p -= 1
                v_in = self.edge(p)
            vert_angle = (v_in[1] >= 0) == (v_out[1] <= 0)
            if self.hor_raycast_edge(n, point, include_start=not vert_angle, include_end=False):
                c += 1
        return c

    def collide(self, other):
        """
        Check if two polygons intersect.
        (Uses Gilbert-Johnson-Keerthi algorithm)
        """
        other = Polygon(other)
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
            elif data[1] < other.r:
                inter = True
                dis = other.r - data[1]
            else:
                inter = False
                dis = data[1] - other.r
            vec.length = dis
            return dis, inter, vec
        else:
            return self.GJK(other)

    def GJK(self, other):
        """
        Call Gilbert-Johnson-Keerthi algorithm and return distance/penetration depth of two polygons,
        check if two polygons intersect and compute vector, by which other should be moved to stop/start intersecting

        Return
           - distance/depth
           - bool(polygons intersect)
           - penetration vector
        """
        other = Polygon(other)
        cso = self.minkowski(-other)
        cso.convex()
        data = cso.nearest_point([0, 0])
        return data[1], [0, 0] in cso, data[0]

    def __getitem__(self, ind):
        return Vec2d(self.points[(1 if ind >= 0 else -1) * abs(ind) % (len(self))])

    def __setitem__(self, ind, value):
        self.points[ind] = Vec2d(value)

    def __delitem__(self, ind):
        del self.points[ind]

    def __iter__(self):
        return iter(self.points)

    def __neg__(self):
        return Polygon(*[-point for point in self])

    def __len__(self):
        return len(self.points)

    def __repr__(self):
        return 'Polygon({0})'.format('; '.join('[{0}, {1}]'.format(*point) for point in self))

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
            return abs(dif), dif > 0, to_other
        else:
            data = Polygon(other).collision_data(self)
            return data[0], data[1], -data[2]

    def draw(self, surface, color=(255, 0, 0), width=1):
        pygame.draw.circle(surface, color, [int(self.center[0]), int(self.center[1])], int(self.r), width)
