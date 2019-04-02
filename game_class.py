import pygame
import pymunk
from geometry import Vec2d
from base_class import PhysObject
from config import *
import math


class BaseShip(PhysObject):
    SIZE_INC = 1
    IMAGE_SHIFT = Vec2d(0, 0)

    def __init__(self):
        super().__init__()
        self.draw_layer = DRAW_LAYER.SHIP
        self.weapons = []
        self.engines = []
        self.components = []

    def image_to_local(self, pos):
        return Vec2d(pos) * self.SIZE_INC + self.IMAGE_SHIFT

    def mount_to(self, obj, pos):
        obj.mount(self)
        obj.local_pos = pos
        self.components.append(obj)


class Component(PhysObject):
    SIZE_INC = 1
    IMAGE_SHIFT = Vec2d(0, 0)

    def __init__(self):
        super().__init__()
        self.draw_layer = DRAW_LAYER.COMPONENT
        self._pos = Vec2d(0, 0)
        self._ang = 0
        self._parent = None
        self._i_shape = None
        self._i_body = None

    def image_to_local(self, pos):
        return pos * self.SIZE_INC + self.IMAGE_SHIFT

    def mounted(self):
        return self._parent is not None

    def mount(self, parent):
        self._parent = parent
        self.body = parent.body

    def unmount(self):
        if self.mounted():
            pos = self.pos
            ang = self.ang
            self._parent = None
            if self._space:
                self._space.add(self._i_body)
            self.body = self._i_body
            self.set_local_placement((0, 0), 0)
            self.pos = pos
            self.ang = ang

    @property
    def space(self):
        return self._space

    @space.setter
    def space(self, space):
        # shapes ???
        own_body = self._body is not None and self._body is self._i_body
        if self._space is not None:
            if self._shape:
                self._space.remove(self._shape)
            if own_body:
                self._space.remove(self._body)
        self._space = space
        if space is not None:
            if own_body:
                space.add(self._body)
            if self._shape is not None:
                space.add(self._shape)

    @property
    def source_shape(self):
        return self._i_shape

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape):
        i_shape = shape.copy()
        i_space = i_shape.space
        if i_space:
            i_space.remove(i_shape)
        i_shape.body = None
        self._i_shape = i_shape
        if shape.space:
            shape.space.remove(shape)
        if shape.body is not self._body:
            shape.body = self._body
        if self._space is not None:
            if self._shape is not None:
                self._space.remove(self._shape)
            self._space.add(shape)
        self._shape = shape
        self.update_local_placement()

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, body):
        self.space = None
        self._body = None
        if self._i_shape is not None:
            self._shape.body = body
        self.space = body.space
        self._body = body
        self.apply_rect()

    def update_local_placement(self):
        pos, ang = self.local_pos, self.local_angle
        i_shape = self._i_shape
        shape = self._shape
        if isinstance(i_shape, pymunk.Poly):
            shape.unsafe_set_vertices((e + pos for e in i_shape.get_vertices()))
        elif isinstance(i_shape, pymunk.Segment):
            shape.unsafe_set_endpoints(i_shape.a + pos, i_shape.b + pos)
        elif isinstance(i_shape, pymunk.Circle):
            shape.unsafe_set_offset(Vec2d(pos) + self._i_shape.offset)

    def set_local_placement(self, pos, ang):
        self._pos, self._ang = Vec2d(pos), ang
        self.update_local_placement()

    @property
    def local_pos(self):
        return self._pos

    @local_pos.setter
    def local_pos(self, pos):
        self._pos = Vec2d(pos)
        self.update_local_placement()

    @property
    def local_angle(self):
        return self._ang

    @local_angle.setter
    def local_angle(self, ang):
        self._ang = ang
        self.update_local_placement()

    def _get_pos(self):
        return self.local_to_world(self._pos)

    def _set_pos(self, p):
        if not self.mounted():
            self._rect.center = p
            self._body.position = p
    pos, center = property(_get_pos, _set_pos), property(_get_pos, _set_pos)

    def _get_angle(self):
        return self._body.angle / math.pi * 180 + self._ang

    def _set_angle(self, ang):
        if self.mounted():
            self._ang = ang - self._body.angle / math.pi * 180
        else:
            self._body.angle = ang / 180 * math.pi
        self.update_local_placement()
    ang, angle = property(_get_angle, _set_angle), property(_get_angle, _set_angle)

    def apply_rect(self):
        self._rect.center = self.local_to_world(self._pos)


class BaseEngine(Component):

    def __init__(self):
        super().__init__()
        self.draw_layer = DRAW_LAYER.ENGINE


if __name__ == '__main__':
    from main_loop import Main
    from base_class import PhysicsGroup, Level
    drag_sprite = None
    main = Main()
    import random


    class TestLevel(Level):

        def pregenerate(self):
            space = pymunk.Space()
            space.gravity = [0, 0]

            group = PhysicsGroup(space)
            from Ships.Vessel import Ship
            from Engines.red_small_booster import Engine
            ship = Ship()
            ship.pos = (50, 50)
            ship.add(group)
            self.ship = ship
            engine = Engine()
            engine.pos = (100, 100)
            engine.add(group)
            self.engine = engine
            # ship.mount_to(engine, ship.image_to_local((690, 395)))

            self.groups.append(group)

        def pregenerate2(self):
            space = pymunk.Space()
            def begin(arbiter, space, dct):
                print(arbiter)
                return True
            space.add_wildcard_collision_handler(3).begin = begin
            space.gravity = [0, 1000]

            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            shape = pymunk.Segment(body, [0, self.size[1]], [self.size[0], self.size[1]], 10)
            space.add(body, shape)

            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            shape = pymunk.Segment(body, [0, 0], [0, self.size[1]], 0)
            space.add(body, shape)

            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            shape = pymunk.Segment(body, [self.size[0], 0], [self.size[0], self.size[1]], 10)
            space.add(body, shape)

            group = PhysicsGroup(space)
            from Ships.Vessel import Ship
            from Engines.red_small_booster import Engine
            ship = Ship()
            ship.pos = [10, 100]
            ship.add(group)
            self.ship = ship
            engine = Engine()
            engine.pos = (100, 100)
            engine.add(group)
            self.engine = engine
            for n in range(20):
                size = 100
                sprite = PhysObject()
                sprite.image = pygame.Surface([size] * 2).convert_alpha()
                sprite.image.fill((0, 0, 0, 0))
                pygame.draw.circle(sprite.image, (0, 0, 255), [size // 2] * 2, size // 2)
                sprite.rect = sprite.image.get_rect()
                sprite.body = pymunk.Body()
                sprite.shape = pymunk.Circle(sprite.body, size // 2)
                sprite.shape.density = 1

                sprite.pos = [random.randint(0, self.size[0]), random.randint(0, self.size[1])]
                sprite.vel = [10, 0]
                group.add(sprite)
                sprite.shape.friction = 1
                if n == 0:
                    sprite.pos = [0, 0]
                    pygame.draw.circle(sprite.image, (0, 255, 0), [size // 2] * 2, size // 2)
                    pygame.draw.line(sprite.image, (255, 0, 0), [size // 2] * 2, [size, size // 2])
                    group.uni = sprite

            self.groups.append(group)

        def get_mouse_sprite(self):
            for s in self.groups[0].sprites():
                if s.shape.point_query(self.mouse_absolute)[0] <= 0:
                    return s
            return None

        def send_event(self, event):
            super().send_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    global drag_sprite
                    if drag_sprite is None:
                        s = self.get_mouse_sprite()
                        if s is not None:
                            drag_sprite = s
                    else:
                        drag_sprite.vel = (self.mouse_absolute - self.mouse_absolute_prev) / self.step_time * 1000
                        drag_sprite = None
                elif event.button == 2:
                    s = self.get_mouse_sprite()
                    if s is not None:
                        s.vel = [0, -500]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    if self.engine.mounted():
                        self.engine.unmount()
                    else:
                        self.ship.mount_to(self.engine, (-40, 0))
                        self.engine.local_angle = 90
                elif event.key == pygame.K_i:
                    print(self.engine.velocity, self.engine.pos)
                    self.engine.pos = [300, 300]
                    self.engine.vel = [0, 0]

        def end_step(self):
            super().end_step()
            global drag_sprite
            # print(drag_sprite, self.mouse_absolute)
            if drag_sprite is not None:
                drag_sprite.pos = self.mouse_absolute
                drag_sprite.vel = [0, 0]

        def handle_keys(self):
            super().handle_keys()

        def draw(self, surface):
            super().draw(surface)
            shape = self.ship.shape
            vert = shape.get_vertices()
            ang = self.ship.angle
            for n in range(-1, len(vert) - 1):
                a_s = Vec2d(vert[n]).rotated(ang) + self.ship.pos
                a_e = Vec2d(vert[n + 1]).rotated(ang) + self.ship.pos
                pygame.draw.line(surface, (255, 0, 0),
                                 self.camera.world_to_local(a_s),
                                 self.camera.world_to_local(a_e))
            pygame.draw.circle(surface, (255, 0, 0), self.camera.world_to_local(self.ship.IMAGE_SHIFT +
                                                                                self.ship.pos).int(), 3)
            pygame.draw.circle(surface, (255, 255, 0), self.camera.world_to_local(
                                                                                self.ship.pos).int(), 3)


    main.size = [800, 600]
    level = TestLevel([2000, 1500], [800, 600])

    main.load_level(level)
    main.start()
