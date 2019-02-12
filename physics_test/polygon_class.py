import pygame
from physics_test.vec2d import Vec2d
from random import randint


def normalize_angle(ang):
    if ang < 0:
        ang = 360 - abs(ang) % 360
    if ang > 360:
        ang %= 360
    return ang


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
    polys = []

    def __init__(self, *points, user=False):
        """
        Clockwise point sorting
        """
        first = points[0]
        if isinstance(first, Polygon):
            points = first.points
        elif isinstance(first, pygame.Rect):
            points = [first.bottomright, first.bottomleft, first.topleft, first.topright]
        self.points = [Vec2d(point) for point in points]
        if user:
            self.polys.append(self)

    def copy(self):
        return Polygon(*[Vec2d(point) for point in self])

    def sort(self, clockwise=True):
        center = self.center()
        self.points.sort(key=lambda p: normalize_angle((p - center).get_angle()),
                         reverse=clockwise)

    def sorted(self, clockwise=True):
        new = self.copy()
        new.sort(clockwise)
        return new

    def convex(self):
        """
        Make polygon convex depending on outer points
        """
        marked = []
        for n, p in enumerate(self.get_points()):
            poly = self.copy()
            del poly[n]
            if p in poly:
                marked.append(n)
        for n in marked[::-1]:
            del self[n]

    def is_convex(self):
        for n, p in enumerate(self):
            poly = self.copy()
            del poly[n]
            if p in poly:
                return False
        return True

    def convexed(self):
        new = self.copy()
        new.convex()
        return new

    def shift(self, shift):
        for point in self.points:
            point += shift

    def shifted(self, shift):
        new = self.copy()
        new.shift(shift)
        return new

    def move(self, pos, point=None):
        if point is None:
            point = self.center()
        self.shift(Vec2d(pos) - point)

    def moved(self, pos, point=None):
        if point is None:
            point = self.center()
        return self.shifted(Vec2d(pos) - point)

    def rotate(self, ang, pos=None):
        """
        Clockwise rotation angle in degrees
        """
        if pos is None:
            pos = self.center()
        for n, p in enumerate(self):
            vec_to = p - pos
            self[n] = pos + vec_to.rotated(ang)

    def rotated(self, ang, pos=None):
        new = self.copy()
        new.rotate(ang, pos)
        return new

    def get_points(self):
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

    def center(self):
        x, y = 0, 0
        n = 1
        for n, p in enumerate(self, 1):
            x += p[0]
            y += p[1]
        return Vec2d(x / n, y / n)

    def bounding(self, center=None, return_pygame=False):
        """
        Return bounding rectangle build around point (default = polygon center)
        """
        def get_x(e):
            return e[0]

        def get_y(e):
            return e[1]

        left = min(self, key=get_x)[0]
        right = max(self, key=get_x)[0]
        top = max(self, key=get_y)[1]
        bottom = min(self, key=get_y)[1]
        if center is not None:
            mdx = max([left, right], key=lambda e: abs(center[0] - e))
            left, right = center[0] - mdx, center[1] + mdx
            mdy = max([top, bottom], key=lambda e: abs(center[1] - e))
            top, bottom = center[1] + mdy, center[1] - mdy
        if return_pygame:
            return pygame.Rect(left, bottom, right - left, top - bottom)
        else:
            return [Vec2d(left, top), Vec2d(right, bottom)]

    def contains(self, point, crossing=True):
        return self.__contains__(point, crossing)

    def __contains__(self, point, crossing=True):
        if Vec2d(point) in self.points:
            return True
        else:
            if crossing:
                return self.horizontal_intersection_num(point) % 2 == 1
            else:
                return abs(self.winding(point)) == 1

    def nearest_line(self, point):
        """
        Return edge index assuming that INFINITE LINE build on it would be the nearest to the point from others
        """
        mx = [None, None]
        for n, p in enumerate(self):
            edge = self.edge(n)
            to_point = point - p
            proj_y = to_point.projection(edge.perpendicular()).get_length_sqrd()
            if mx[1] is None or proj_y < mx[1]:
                mx[0] = n
                mx[1] = proj_y
        return mx[0]

    def minkowski(self, other):
        """
        UNSORTED AND UNFILTERED Minkowski addiction
        Call convex() after sorting clockwise for resulting Minkowski polygon
        """
        points = []
        for p1 in self:
            for p2 in other:
                points.append(Vec2d(p1 + p2))
        return Polygon(*points)

    def winding(self, wp):
        """
        Winding number of polygon around point
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
        Check if horizontal ray from point intersects edge
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
        How much edges horizontal to-right ray from point would intersect
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

    def __getitem__(self, ind):
        return Vec2d(self.points[(1 if ind >= 0 else -1) * abs(ind) % (len(self))])

    def __setitem__(self, ind, value):
        self.points[ind] = value

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
        pygame.draw.polygon(surface, color, [list(point) for point in self.points], width)


if __name__ == '__main__':
    pygame.init()

    size = [800, 800]

    screen_real = pygame.display.set_mode(size)
    screen = pygame.Surface(size)
    p1, p2 = Polygon([0, 0], [0, 100], [90, 60], user=True), Polygon([0, 0], [0, 60], [-30, 30])
    p1.shift([100, 50])
    p2.shift([100, 400])
    p2 = p1.rotated(90, p1.bounding(return_pygame=True).topleft)
    msm = p1.minkowski(-p2).sorted()
    msm_con = msm.convexed()
    # Polygon.polys.append(msm_con)
    Polygon.polys.append(p2)
    Polygon.polys.append(msm)
    cols = [[randint(0, 4) * 63, randint(0, 4) * 63, randint(0, 4) * 63] for _ in Polygon.polys]
    poly = None

    running = True
    flip = True
    while running:
        ms = [pygame.mouse.get_pos()[0], size[1] - pygame.mouse.get_pos()[1]] if flip else pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if poly is not None:
                    poly = None
                elif event.button == 1:
                    for p in Polygon.polys:
                        if ms in p:
                            poly = p
                            break
                elif event.button == 3:
                    print(msm.nearest_line(ms))
        if poly is not None:
            poly.move(ms)
            msm.set_points(p1.minkowski(-p2).sorted().convexed())

        screen.fill((255, 255, 255))
        # p1.draw(screen)
        # p2.draw(screen, (0, 255, 0))
        # msm.draw(screen, (0, 0, 255))
        # for i in msm.points + [msm.center()]:
        #     pygame.draw.circle(screen, (0, 0, 255), [int(e) for e in i], 3)
        # msm_con.draw(screen, (255, 0, 255))
        # pygame.draw.line(screen, (0, 0, 0), [ms[0] - 200, ms[1]], [ms[0] + 200, ms[1]])
        # pygame.draw.rect(screen, (255, 0, 0), [ms[0], ms[1] - 1, 1, 3])
        for n, p in enumerate(Polygon.polys):
            p.draw(screen, cols[n])
        for n in range(len(msm)):
            p = msm[n]
            vec = msm.edge(n)
            to_p = ms - p
            pygame.draw.line(screen, (128, 128, 128), p, p + vec.perpendicular())
            pygame.draw.line(screen, (0, 0, 255), p, p + to_p.projection(vec.perpendicular()))
        screen_real.blit(pygame.transform.flip(screen, False, flip), (0, 0))

        pygame.display.flip()

    pygame.quit()
