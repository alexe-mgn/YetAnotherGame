import pygame
import pymunk


def draw_debug(camera, surface, sprites):
    rect = camera.get_rect()
    tl = rect.topleft
    zoom = camera.get_current_zoom()

    def w_to_l(pos):
        return [int(e) for e in (pos - tl) * zoom]

    for s in sprites:
        pos, ang = s.pos, s.angle
        shape = s.shape
        if isinstance(shape, pymunk.Poly):
            pygame.draw.polygon(surface, (255, 0, 0),
                                [w_to_l(e.rotated_degrees(ang) + pos) for e in shape.get_vertices()],
                                2)
        elif isinstance(shape, pymunk.Segment):
            pygame.draw.line(surface, (255, 0, 0),
                             w_to_l(shape.a.rotate_degrees(ang) + pos), w_to_l(shape.b.rotated_degrees(ang) + pos),
                             (shape.radius * zoom))
        elif isinstance(shape, pymunk.Circle):
            pygame.draw.circle(surface, (255, 0, 0),
                               w_to_l(pos + getattr(
                                   getattr(s, '_i_shape', None),
                                   'offset',
                                   pymunk.Vec2d(0, 0)).rotated_degrees(ang)),
                               int(shape.radius * zoom), 2)
        pygame.draw.circle(surface, (0, 0, 255), w_to_l(pos), 3)
