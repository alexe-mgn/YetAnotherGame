import pygame
import pymunk
from geometry import Vec2d, FRect, normalized_angle
from physics import PhysObject
from loading import GObject
from config import *
import math


class ImageHandler(PhysObject):
    draw_layer = 0
    size_inc = SIZE_COEF
    IMAGE_SHIFT = Vec2d(0, 0)
    team = TEAM.NEUTRAL

    def __init__(self, obj=None):
        super().__init__()
        if obj is None:
            self._image = GObject(self._frames)
        else:
            self._image = obj
        size = self._image.get_size()
        a = (size[0] ** 2 + size[1] ** 2) ** .5
        self.rect = FRect(0, 0, 0, 0)
        self.rect.inflate_ip(a, a)

    def end_step(self):
        super().end_step()
        self._image.update(self.step_time)

    @classmethod
    def image_to_local(cls, pos):
        return Vec2d(pos) * cls.size_inc + cls.IMAGE_SHIFT

    @property
    def image(self):
        return self._image.read()


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
        if not self.object and (self.allowed is True or getattr(obj, 'role', None) in self.allowed):
            self.object = obj
            self.role = obj.role
            obj.mount(self.parent)
            obj.set_local_placement(self._pos, self._ang)
            obj.draw_layer = DRAW_LAYER.CREATURE_TOP if self.top else DRAW_LAYER.CREATURE_BOTTOM
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

    def __bool__(self):
        return self.object is not None


class BaseProjectile(ImageHandler):
    draw_layer = DRAW_LAYER.PROJECTILE
    lifetime = 1000
    st_velocity = 1000

    def __init__(self):
        super().__init__()
        self.lifetime = 1000
        self.life_left = self.lifetime
        self.parent = None

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape):
        if shape.space:
            shape.space.remove(shape)
        if shape.body is not self._body:
            shape.body = self._body
        if self._space is not None:
            if self._shape is not None:
                self._space.remove(self._shape)
            self._space.add(shape)
        self._shape = shape
        shape.collision_type = COLLISION_TYPE.PROJECTILE

    # BODY SHAPES !!!

    def fire(self, ang):
        rad = math.radians(ang)
        vec = Vec2d(self.st_velocity * math.cos(rad), self.st_velocity * math.sin(rad))
        self.velocity = vec
        self.angle = ang

    def collideable(self, obj):
        return obj.team != self.team

    def end_step(self):
        super().end_step()
        self.life_left -= self.step_time
        if self.life_left <= 0:
            self.kill()


class BaseCreature(ImageHandler):
    draw_layer = DRAW_LAYER.CREATURE

    def __init__(self):
        super().__init__()

        self.mounts = []
        self.mounts_names = {}

    def get_mount(self, index=None, key=None):
        if index is not None:
            m = self.mounts[index]
        elif key is not None:
            m = self.mounts[self.mounts_names[key]]
        return m

    def mount(self, obj, index=None, key=None):
        m = self.get_mount(index, key)
        s = m.mount(obj)
        if s:
            obj.team = self.team
            obj.activate()
        return s

    def unmount(self, index=None, key=None):
        m = self.get_mount(index, key)
        o = m.object
        s = m.unmount()
        if s:
            o.team = TEAM.DEFAULT
            o.deactivate()
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

    def get_weapons(self):
        return [e.object for e in self.mounts if e.role == ROLE.WEAPON]

    def get_engines(self):
        return [e.object for e in self.mounts if e.role == ROLE.ENGINE]

    def walk(self, vec):
        engine = self.get_mount(key='engine')
        if engine:
            engine.object.walk(vec)


class BaseComponent(ImageHandler):
    draw_layer = DRAW_LAYER.COMPONENT
    role = ROLE.COMPONENT

    def __init__(self):
        super().__init__()

        self._pos = Vec2d(0, 0)
        self._ang = 0
        self._parent = None
        self._i_shape = None
        self._i_body = None
        self.activated = False

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

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    @property
    def space(self):
        return self._space

    @space.setter
    def space(self, space):
        # shapes ???
        own_body = self._body is not None and self._body is self._i_body
        shapes = self.shapes
        if self._space is not None:
            if shapes:
                self._space.remove(*shapes)
            if own_body:
                self._space.remove(self._body)
        self._space = space
        if space is not None:
            if own_body:
                space.add(self._body)
            if shapes:
                space.add(shapes)

    @property
    def source_shape(self):
        return self._i_shape

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, shape):
        if shape.space:
            shape.space.remove(shape)
        shape.body = None
        self._i_shape = shape.copy()
        shape.body = self._body
        if self._space is not None:
            if self._shape is not None:
                self._space.remove(self._shape)
            self._space.add(shape)
        self._shape = shape
        self.update_local_placement()

    @property
    def shapes(self):
        shape = self.shape
        return [shape] if shape is not None else []

    def own_body(self):
        return self.body is self.i_body

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

    @property
    def i_body(self):
        return self._i_body

    @i_body.setter
    def i_body(self, body):
        if self.own_body():
            self.body = body
        if self._i_body:
            self._i_body.sprite = None
        self._i_body = body
        body.sprite = self

    def update_local_placement(self):
        pos, ang = self.local_pos, self.local_angle
        i_shape = self._i_shape
        shape = self._shape
        if isinstance(i_shape, pymunk.Poly):
            shape.unsafe_set_vertices([e + pos for e in i_shape.get_vertices()])
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

    def apply_damping(self):
        if self.own_body() and self.height <= 0 and self.damping:
            self.velocity *= (1 - self.damping)


class BaseEngine(BaseComponent):
    draw_layer = DRAW_LAYER.CREATURE_BOTTOM
    role = ROLE.ENGINE

    engine_force = 100 * MASS_COEF
    max_vel = 100 * SIZE_COEF
    max_fps = 10

    def __init__(self):
        super().__init__()
        self._image.fps = 0

    def walk(self, vec):
        if any(vec):
            tv = Vec2d(vec)
            tv.length = self.max_vel
            cv = self.vel
            dif = tv - cv
            dif.length = self.engine_force
            self._body.force += dif

    def end_step(self):
        super().end_step()
        if self.activated:
            vel = self.velocity
            self._image.fps = self.max_fps * vel.length / self.max_vel
            self.angle = math.degrees(vel.angle)


class BaseWeapon(BaseComponent):
    draw_layer = DRAW_LAYER.WEAPON
    role = ROLE.WEAPON
    fire_pos = Vec2d(0, 0)

    def fire(self):
        proj = self.Projectile()
        proj.add(*self.groups())
        proj.parent = self
        proj.team = self.team
        proj.pos = self.local_to_world(self.fire_pos)
        proj.fire(self.angle)


if __name__ == '__main__':
    from main_loop import Main
    from interface import Level
    from physics import PhysicsGroup

    drag_sprite = None
    main = Main()
    import random
    from Projectiles.Pulson import Projectile


    class TestLevel(Level):

        def pregenerate(self):
            space = pymunk.Space()
            space.gravity = [0, 0]

            group = PhysicsGroup(space)
            from Weapons.Pulson import Weapon
            w = Weapon()
            w.add(group)
            w.pos = (300, 300)
            self.w = w
            w = Weapon()
            w.add(group)
            w.pos = (300, 300)
            from Creatures.MechZero import Creature
            from Components.LegsZero import Engine
            mc = Creature()
            mc.add(group)
            mc.pos = (500, 500)
            ls = Engine()
            ls.add(group)
            ls.pos = (300, 300)
            mc.mount(ls, key='engine')

            self.player = mc

            self.groups.append(group)

        def get_mouse_sprite(self):
            for s in self.groups[0].layer_sorted()[::-1]:
                if s.shape.point_query(self.mouse_absolute)[0] <= 0:
                    return s
            return None

        def send_event(self, event):
            super().send_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                global drag_sprite
                s = self.get_mouse_sprite()
                if event.button == 1:
                    if drag_sprite is not None:
                        drag_sprite.vel = (self.mouse_absolute - self.mouse_absolute_prev) / self.step_time * 1000
                        drag_sprite = None
                    elif s is not None:
                        if drag_sprite is None:
                            drag_sprite = s
                elif event.button == 2:
                    if hasattr(s, 'fire'):
                        s.fire()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    proj = Projectile()
                    proj.add(self.groups[0])
                    proj.fire(self.mouse_absolute.angle)
                elif event.key == pygame.K_g:
                    self.w.fire()

        def end_step(self):
            super().end_step()
            global drag_sprite
            # print(drag_sprite, self.mouse_absolute)
            if drag_sprite is not None:
                if drag_sprite.space:
                    drag_sprite.pos = self.mouse_absolute
                    drag_sprite.vel = [0, 0]
                else:
                    drag_sprite = None

        def handle_keys(self):
            super().handle_keys()

        def draw(self, surface):
            super().draw(surface)


    main.size = [800, 600]
    level = TestLevel([6000, 6000], [800, 600])

    main.load_level(level)
    main.start()
