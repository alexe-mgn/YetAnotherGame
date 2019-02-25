import pygame
from physics_test.vec2d import Vec2d
from random import randint
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
            points = [first.bottomright, first.bottomleft, first.topleft, first.topright]
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
        Uses self.GJK(other)
        Check Polygon.GJK
        """
        if isinstance(other, Circle):
            data = self.nearest_point(other.center)
            if not data[3]:
                vec = self.edge(data[2]).perpendicular()
            else:
                vec = other.center - self[data[2]]
            # if data[0] == other.center:
            #     dis = other.r
            #     vec.length = dis
            #     print(1)
            #     return dis, True, vec
            if self.contains(other.center):
                inter = True
                dis = data[1] + other.r
            elif data[1] < other.r:
                inter = True
                dis = other.r - data[1]
            else:
                inter = False
                dis = data[1] - other.r
            print(inter, dis)
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
           - vector
        """
        other = Polygon(other)
        cso = self.minkowski(-other)
        cso.convex()
        data = cso.nearest_point([0, 0])
        pygame.draw.line(screen, (255, 0, 0), [0, 0], data[0], 1)
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
                p = Polygon(pos)
                pos = p.center
                r = (max(p, key=lambda p: (p - pos).get_length_sqrd()) - pos).length
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
        if isinstance(other, Circle):
            t = self.r + other.r
            to_other = other.pos - self.pos
            dif = to_other.length - t
            to_other.length = dif
            return abs(dif), dif < 0, to_other
        else:
            data = Polygon(other).collision_data(self)
            return data[0], data[1], -data[2]

    def draw(self, surface, color=(255, 0, 0), width=1):
        pygame.draw.circle(surface, color, [int(self.center[0]), int(self.center[1])], int(self.r), width)


if __name__ == '__main__':
    pygame.init()

    size = [800, 800]
    font = pygame.font.SysFont(None, 50)

    screen_real = pygame.display.set_mode(size)
    screen = pygame.Surface(size)
    p1, p2 = Polygon([0, 0], [0, 100], [90, 60], user=True), Polygon([0, 0], [0, 60], [-30, 30])
    p1.shift([100, 50])
    p2.shift([100, 400])
    p2 = p1.rotated(90, p1.bounding(return_pygame=True).topleft)
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
                    print(msm.nearest_edge(ms))
                    print(p1.collide(p2))
                elif event.button == 4:
                    if poly is not None:
                        poly.rotate(10)
                elif event.button == 5:
                    if poly is not None:
                        poly.rotate(-10)
                elif event.button == 2:
                    ruler = ms
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    ruler = None
        if poly is not None:
            poly.move(ms)
            msm.set_points(p1.minkowski(-p2).convexed())

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
        # p1.draw(screen)
        # p2.draw(screen, (0, 255, 0))
        # msm.draw(screen, (0, 0, 255))
        # for i in msm.points + [msm.center]:
        #     pygame.draw.circle(screen, (0, 0, 255), [int(e) for e in i], 3)
        # msm_con.draw(screen, (255, 0, 255))
        # pygame.draw.line(screen, (0, 0, 0), [ms[0] - 200, ms[1]], [ms[0] + 200, ms[1]])
        # pygame.draw.rect(screen, (255, 0, 0), [ms[0], ms[1] - 1, 1, 3])
        # Polygon(msm.maximum_bounding(return_pygame=True)).draw(screen)
        p2.draw(screen)
        c = Circle(p2)
        inter = p1.collision_data(c)
        if inter[1] or pressed[pygame.K_z]:
            p2.shift(inter[2])
            c.move(inter[2])
        c.draw(screen)
        for n, p in enumerate(Polygon.polys):
            p.draw(screen, cols[n])
        for n in range(len(msm)):
            p = msm[n]
            vec = msm.edge(n)
            to_p = ms - p
            pygame.draw.line(screen, (128, 128, 128), p, p + vec.perpendicular())
            pygame.draw.line(screen, (0, 0, 255), p, p + to_p.projection(vec.perpendicular()))
        np = msm.nearest_point(ms)[0]
        pygame.draw.circle(screen, (255, 0, 0), [int(e) for e in np], 5)
        screen_real.blit(pygame.transform.flip(screen, False, flip), (0, 0))

        pygame.display.flip()

    pygame.quit()
