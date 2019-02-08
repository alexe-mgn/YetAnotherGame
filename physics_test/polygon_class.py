import pygame
from vec2d import Vec2d
import sys

def normalize_angle(ang):
    if ang < 0:
        ang = 360 - abs(ang) % 360
    if ang > 360:
        ang %= 360
    return ang


class Polygon:

    def __init__(self, *points):
        if isinstance(points[0], Polygon):
            self.points = points[0].copy()
        else:
            self.points = [Vec2d(point) for point in points]

    def draw(self, surface, color=(255, 0, 0), width=1):
        pygame.draw.polygon(surface, color, [list(point) for point in self.points], width)

    def copy(self):
        return Polygon(*[Vec2d(point) for point in self])

    def wise_sort(self):
        center = self.center()
        self.points.sort(key=lambda p: normalize_angle((p - center).get_angle()), reverse=True)

    def move(self, shift):
        for point in self.points:
            point += shift

    def center(self):
        x, y = 0, 0
        n = 1
        for n, p in enumerate(self, 1):
            x += p[0]
            y += p[1]
        return Vec2d(x / n, y / n)

    def __contains__(self, item):
        if Vec2d(item) in self.points:
            return True
        

    def minkowski(self, other):
        points = []
        for p1 in self:
            for p2 in other:
                    points.append(Vec2d(p1 + p2))
        msm = Polygon(*points)
        msm.wise_sort()
        return msm

    def __getitem__(self, ind):
        return Vec2d(self.points[ind])

    def __len__(self):
        return len(self.points)

    def __repr__(self):
        return 'Polygon({0})'.format('; '.join('[{0}, {1}]'.format(*point) for point in self))


if __name__ == '__main__':
    pygame.init()

    size = [800, 800]

    screen = pygame.display.set_mode(size)
    p1, p2 = Polygon([0, 0], [0, 60], [30, 30]), Polygon([0, 0], [0, 60], [-30, 30])
    p1.move([100, 50])
    p2.move([100, 400])
    msm = p1.minkowski(p2)
    print(msm)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass

        screen.fill((255, 255, 255))
        p1.draw(screen)
        p2.draw(screen, (0, 255, 0))
        msm.draw(screen, (0, 0, 255))

        pygame.display.flip()

    pygame.quit()