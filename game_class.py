import pygame
import pymunk
from geometry import Vec2d, FRect, normalized_angle
from physics import PhysObject
from config import *
import math


class ImageHandler(PhysObject):
    draw_layer = 0
    SIZE_INC = SIZE_COEF
    IMAGE_SHIFT = Vec2d(0, 0)

    def __init__(self, obj=None):
        super().__init__()
        if obj is None:
            self._image = None
            del self._image
        else:
            self._image = obj
        size = self._image.get_size()
        a = (size[0] ** 2 + size[1] ** 2) ** .5
        self.rect = FRect(0, 0, 0, 0)
        self.rect.inflate_ip(a, a)

    def image_to_local(self, pos):
        return Vec2d(pos) * self.SIZE_INC + self.IMAGE_SHIFT


class Mount:

    def __init__(self, parent, position=None, angle=0, allowed=None, top=True):
        self.parent = parent
        self._pos = Vec2d(0, 0) if position is None else Vec2d(position)
        self._ang = angle
        self.allowed = [] if allowed is None else list(allowed)
        self.object = None
        self.role = None
        self.top = top

    def _get_pos(self):
        return self._pos

    def _set_pos(self, pos):
        if self.object:
            self.object.position = pos
        self._pos = Vec2d(pos)

    pos, position = property(_get_pos, _set_pos), property(_get_pos, _set_pos)

    def _get_angle(self):
        return self._ang

    def _set_angle(self, ang):
        if self.object:
            self.object.angle = ang
        self._ang = ang

    ang, angle = property(_get_angle, _set_angle), property(_get_angle, _set_angle)

    def mount(self, obj):
        if not self.object and (self.allowed[0] is True or getattr(obj, 'role', None) in self.allowed):
            self.object = obj
            self.role = obj.role
            obj.mount(self.parent)
            obj.set_local_placement(self._pos, self._ang)
            obj.draw_layer = DRAW_LAYER.SHIP_TOP if self.top else DRAW_LAYER.SHIP_BOTTOM
            if self.role == ROLE.ENGINE:
                force = obj.force
                self.boost_vec = Vec2d(force * math.cos(math.radians(self._ang)), force * math.sin(math.radians(
                    self._ang)))
            return True
        else:
            return False

    def unmount(self):
        if self.object:
            self.object.unmount()
            del self.object.draw_layer
            self.object = None
            self.role = None
            return True
        else:
            return False


class BaseProjectile(ImageHandler):
    draw_layer = DRAW_LAYER.PROJECTILE

    def __init__(self):
        super().__init__()
        self.team = TEAM.ENEMY

    @property
    def shape(self):
        return super().shape

    @shape.setter
    def shape(self, shape):
        super().shape = shape
        shape.collision_type = COLLISION_TYPE.PROJECTILE
    # BODY SHAPES !!!


class BaseShip(ImageHandler):
    draw_layer = DRAW_LAYER.SHIP

    def __init__(self):
        super().__init__()

        self.mounts = []
        self.mounts_names = {}
        self._boost_map = [[0, 0], [0, 0]]

    def mount(self, obj, index=None, key=None):
        print(obj)
        if index is not None:
            m = self.mounts[index]
        elif key is not None:
            m = self.mounts[self.mounts_names[key]]
        if obj.role == ROLE.ENGINE:
            self.recalculate_boost_map()
        s = m.mount(obj)
        return s

    def unmount(self, index=None, key=None):
        if index is not None:
            m = self.mounts[index]
        elif key is not None:
            m = self.mounts[self.mounts_names[key]]
        if m.role == ROLE.ENGINE:
            self.recalculate_boost_map()
        s = m.unmount()
        return s

    def init_mounts(self, *mounts):
        shift = len(self.mounts)
        for n, i in enumerate(mounts):
            if hasattr(i, '__iter__'):
                v, k = i
                self.mounts_names[k] = shift + n
            else:
                v = i
            self.mounts.append(v)

    def get_engines(self):
        return [e.object for e in self.mounts if e.role == ROLE.ENGINE]

    def get_weapons(self):
        return [e.object for e in self.mounts if e.role == ROLE.WEAPON]

    def recalculate_boost_map(self):
        self._boost_map = self.calculate_boost_map()

    def calculate_boost_map(self):
        b_map = [[0, 0], [0, 0]]
        engines = self.get_engines()
        for e in engines:
            ang = e.local_angle
            f = e.max_vector_force(ang)
            b_map[0][0 if f[0] >= 0 else 1] += f[0]
            b_map[1][0 if f[1] >= 0 else 1] += f[1]
        return b_map

    def boost_to(self, pos):
        loc = self.world_to_local(pos)
        tv = (pos - self.pos) / 10
        self.boost_vel(tv)

    def boost_vel(self, t):
        dif = t - self.velocity
        self.boost(t)

    def boost(self, vec):
        b_map = self._boost_map
        self._body.force += (b_map[0][0 if vec[0] > 0 else 1] if vec[0] != 0 else 0,
                             b_map[1][0 if vec[1] >= 0 else 1] if vec[1] != 0 else 0)

    def rotate_to(self, ang):
        dif_l = normalized_angle(ang - self.ang)
        dif_r = 360 - dif_l
        c_vel = self._body

    def disable_engines(self):
        for e in self.get_engines():
            e.k = 0


class Component(ImageHandler):
    draw_layer = DRAW_LAYER.COMPONENT
    role = ROLE.COMPONENT

    def __init__(self):
        super().__init__()

        self._pos = Vec2d(0, 0)
        self._ang = 0
        self._parent = None
        self._i_shape = None
        self._i_body = None

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
            if self.shapes:
                self._space.remove(*self.shapes)
            if own_body:
                self._space.remove(self._body)
        self._space = space
        if space is not None:
            if own_body:
                space.add(self._body)
            if self.shapes:
                space.add(*self.shapes)

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
    def shapes(self):
        return [self.shape]

    def own_body(self):
        return self._parent is None

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
        self._pos = Vec2d(pos)
        self._ang = ang
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
        return math.degrees(self._body.angle) + self._ang

    def _set_angle(self, ang):
        if self.mounted():
            self._ang = ang - math.degrees(self._body.angle)
        else:
            self._body.angle = math.radians(ang)
        self.update_local_placement()

    ang, angle = property(_get_angle, _set_angle), property(_get_angle, _set_angle)

    def apply_rect(self):
        self._rect.center = self.local_to_world(self._pos)


class BaseEngine(Component):
    draw_layer = DRAW_LAYER.ENGINE
    role = ROLE.ENGINE

    def __init__(self):
        super().__init__()
        self.k = 0
        self.force = 0

    def pre_update(self):
        if self.k > .001:
            self.boost()
        else:
            self.k = 0

    def vector_force(self, ang):
        force = self.force
        k = self.k
        return Vec2d(force * (k * math.cos(math.radians(ang))), force * (k * math.sin(math.radians(ang))))

    def max_vector_force(self, ang):
        force = self.force
        return Vec2d(force * (math.cos(math.radians(ang))), force * (math.sin(math.radians(ang))))

    def boost(self):
        force = self.force
        ang = self._ang
        self._body.apply_force_at_local_point(self.vector_force(self._ang), self._body.center_of_gravity)


class BaseWeapon(Component):
    draw_layer = DRAW_LAYER.WEAPON
    role = ROLE.WEAPON

    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    from main_loop import Main
    from interface import Level
    from physics import PhysicsGroup

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
            from Weapons.Pulson import Weapon
            for ns in range(10):
                ship = Ship()
                ship.pos = (400, 300)
                ship.add(group)
                self.ship = ship
                self.player = ship
                for n in range(len(self.ship.mounts)):
                    engine = Engine()
                    engine.add(group)
                    engine.pos = (400, 400)
                    self.ship.mount(engine, index=n)
                w = Weapon()
                w.add(group)
                w.pos = (300, 300)
                self.w = w
                self.ship.mount(w, key='main_weapon')

            # from loading import GObject, load_frames, cast_frames, load_image
            #
            # class Animation(ImageHandler):
            #
            #     def __init__(self):
            #         super().__init__()
            #         self.body = pymunk.Body()
            #         self.shape = pymunk.Circle(self.body, 10)
            #         self.shape.density = 1
            #
            #     @classmethod
            #     def init_class(cls):
            #         frames = load_frames('Resources\\Sci-fi\\Explosion')
            #         ln = len(frames)
            #         cls._image, cls.IMAGE_SHIFT = cast_frames(frames, [(170, 170)] * ln, [1] * ln)
            #         cls._image = GObject(cls._image)
            #         # cls._image = GObject(pygame.transform.scale(load_image(# 'Resources\\Sci-fi\\explosion\\0000.png'),(500, 500)))
            #
            #     @property
            #     def image(self):
            #         return self._image.read()
            #
            #     def read_image(self):
            #         return pygame.transform.rotate(self.image, -self.angle)
            #
            # Animation.init_class()
            #
            # an = Animation()
            # an.pos = (400, 400)
            # an._image.fps = 30
            # an.add(group)
            # self.an = an

            self.groups.append(group)

        def get_mouse_sprite(self):
            for s in self.groups[0].layer_sorted()[::-1]:
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
                            if s.own_body():
                                drag_sprite = s
                            else:
                                s.k = int(not bool(s.k))
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
                        self.ship.unmount(index=0)
                    else:
                        self.ship.mount(self.engine, index=0)
                elif event.key == pygame.K_MINUS:
                    self.ship.angle -= 10
                elif event.key == pygame.K_EQUALS:
                    self.ship.angle += 10

        def end_step(self):
            super().end_step()
            global drag_sprite
            # print(drag_sprite, self.mouse_absolute)
            if drag_sprite is not None:
                drag_sprite.pos = self.mouse_absolute
                drag_sprite.vel = [0, 0]

        def handle_keys(self):
            super().handle_keys()
            if self.pressed[pygame.K_h]:
                self.ship.boost(self.mouse_absolute - self.ship.pos)
            else:
                pass  # self.ship.disable_engines()

        def draw(self, surface):
            super().draw(surface)
            w_to_l = self.camera.world_to_local
            for i in self.ship.get_engines():
                pygame.draw.line(surface, (255, 0, 0), w_to_l(i.pos), w_to_l(i.pos + i.vector_force(i.angle)))
            # pygame.draw.circle(surface, (255, 0, 0), w_to_l(self.w.local_to_world(self.w.shape.offset)).int(),
            # int(self.w.shape.radius))


    main.size = [800, 600]
    level = TestLevel([6000, 6000], [800, 600])

    main.load_level(level)
    main.start()
