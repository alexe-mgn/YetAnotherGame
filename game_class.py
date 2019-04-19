import pymunk
from geometry import Vec2d, FRect
from physics import PhysObject
from loading import GObject
from config import *
import math


class ImageHandler(PhysObject):
    size_inc = 1
    IMAGE_SHIFT = Vec2d(0, 0)

    def __init__(self, obj=None):
        super().__init__()
        if obj is None:
            self._image = GObject(self._frames)
        else:
            self._image = GObject(obj)
        size = self._image.get_size()
        a = math.sqrt(size[0] * size[0] + size[1] * size[1])
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


class DynamicObject(ImageHandler):
    role = ROLE.OBJECT
    team = TEAM.DEFAULT
    mat = MAT_TYPE.MATERIAL
    max_health = 100

    def __init__(self):
        super().__init__()
        self.health = self.max_health

    def damage(self, val):
        self.health -= val
        if self.health <= 0:
            self.death()

    def death(self):
        self.kill()


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
        if self.object is not None:
            self.object.position = pos
        self._pos = Vec2d(pos)

    pos, position = property(_get_pos, _set_pos), property(_get_pos, _set_pos)

    def _get_angle(self):
        return self._ang

    def _set_angle(self, ang):
        if self.object is not None:
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
        if self.object is not None:
            self.object.unmount()
            del self.object.draw_layer
            self.object = None
            self.role = None
            return True
        else:
            return False

    def mountable(self, obj):
        return self.allowed is True or obj.role in self.allowed

    def mount_ready(self, obj):
        return self.object is None and (self.allowed is True or obj.role in self.allowed)

    def free(self):
        return self.object is None

    def __bool__(self):
        return self.object is not None

    def __repr__(self):
        return '{}.{}({})'.format(self.parent, self.__class__.__name__, self.object)


class BaseProjectile(DynamicObject):
    draw_layer = DRAW_LAYER.PROJECTILE
    lifetime = 1000
    hit_damage = 10

    def __init__(self):
        super().__init__()
        self.life_left = self.lifetime
        self.parent = None
        self.timeout = False

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

    def collideable(self, obj):
        return obj is not self.parent and collide_case(self, obj)

    def end_step(self):
        super().end_step()
        self.life_left -= self.step_time
        if self.life_left <= 0:
            if not self.timeout:
                self.on_life_end()
            self.timeout = True
        else:
            self.timeout = False

    def on_life_end(self):
        self.kill()

    def _get_angle(self):
        return math.degrees(self.velocity.angle)


class BaseCreature(DynamicObject):
    draw_layer = DRAW_LAYER.CREATURE
    max_health = 100

    def __init__(self):
        super().__init__()

        self.mounts = []
        self.mounts_names = {}

    def get_mount(self, index=None, key=None):
        if index is not None:
            return self.mounts[index]
        elif key is not None:
            return self.mounts[self.mounts_names[key]]

    def mount(self, obj, index=None, key=None):
        m = self.get_mount(index, key)
        if m is not None:
            s = m.mount(obj)
            if s:
                obj.team = self.team
                obj.activate()
            return s
        else:
            for m in self.mounts:
                if m.free() and m.mountable(obj):
                    s = m.mount(obj)
                    if s:
                        obj.team = self.team
                        obj.activate()
                        return s
        return False

    def unmount(self, index=None, key=None):
        m = self.get_mount(index, key)
        if m is not None:
            o = m.object
            s = m.unmount()
            if s:
                o.team = TEAM.DEFAULT
                o.deactivate()
            return s
        return False

    def mounted_objects(self):
        return [e.object for e in self.mounts if e.object is not None]

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

    def free_weapon(self):
        for i in self.mounts:
            if i.role == ROLE.WEAPON and i.free():
                return i

    def shot(self):
        for i in self.get_weapons():
            i.shot()

    def get_engines(self):
        return [e.object for e in self.mounts if e.role == ROLE.ENGINE]

    def walk(self, vec):
        engine = self.get_mount(key='engine')
        if engine:
            engine.object.walk(vec)

    def kill(self):
        for n in range(len(self.mounts)):
            self.unmount(index=n)
        super().kill()


class BaseComponent(DynamicObject):
    draw_layer = DRAW_LAYER.COMPONENT
    role = ROLE.COMPONENT
    max_health = 50

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
            if self._space is not None:
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
        if self._space is not space:
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
        if self._i_body is not None:
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
        return self._body.local_to_world(self._pos)

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

    def local_to_world(self, pos):
        return self._body.local_to_world(self.local_pos + pos)

    def world_to_local(self, pos):
        return self._body.world_to_local(pos) - self.local_pos

    def apply_rect(self):
        self._rect.center = self.local_to_world(self._pos)

    def apply_damping(self):
        if self.own_body() and self.height <= 0 and self.damping:
            self.velocity *= (1 - self.damping)


class BaseEngine(BaseComponent):
    draw_layer = DRAW_LAYER.CREATURE_BOTTOM
    role = ROLE.ENGINE

    engine_force = 100
    max_vel = 100
    max_fps = 10

    def __init__(self):
        super().__init__()
        self.working = False
        self._image.fps = 0
        self.parent_default_damping = 0

    def walk(self, vec):
        cv = self.vel
        if any(vec):
            tv = Vec2d(vec)
            tv.length = self.max_vel
            dif = tv - cv
            dif.length = self.engine_force
            self._body.force += dif
            self.working = True
        elif abs(cv[0]) > .01 and abs(cv[1] > .01):
            # stopping
            cv.length = self.engine_force
            self._body.force -= cv
        else:
            self.velocity = (0, 0)

    def end_step(self):
        super().end_step()
        if self.activated and self.max_fps:
            vel = self.velocity
            if any(vel):
                self._image.fps = self.max_fps * vel.length / self.max_vel
                self.angle = math.degrees(vel.angle)
            else:
                self._image.fps = 0
        else:
            self._image.fps = 0
        self.working = False

    def mount(self, parent):
        s = super().mount(parent)
        if s:
            self.parent_default_damping = parent.damping
            parent.damping = 0

    def unmount(self):
        p = self._parent
        s = super().unmount()
        if s:
            p.damping = self.parent_default_damping
            self.parent_default_damping = 0

    @property
    def local_angle(self):
        return self._ang - math.degrees(self._body.angle)

    @local_angle.setter
    def local_angle(self, ang):
        self._ang = math.degrees(self._body.angle) + ang
        self.update_local_placement()

    def _get_angle(self):
        return self._ang

    def _set_angle(self, ang):
        if self.mounted():
            self._ang = ang
        else:
            self._body.angle = math.radians(ang)
        self.update_local_placement()

    ang, angle = property(_get_angle, _set_angle), property(_get_angle, _set_angle)


class BaseWeapon(BaseComponent):
    draw_layer = DRAW_LAYER.WEAPON
    role = ROLE.WEAPON
    fire_pos = Vec2d(0, 0)
    proj_velocity = 1000
    fire_delay = 1000

    def __init__(self):
        super().__init__()
        self.recharge = 0

    def end_step(self):
        super().end_step()
        if self.recharge > 0:
            self.recharge -= self.step_time

    def shot(self):
        if self.recharge <= 0:
            self.force_fire()
            self.recharge = self.fire_delay

    def force_fire(self):
        proj = self.Projectile()
        proj.add(*self.groups())
        proj.parent = self
        proj.team = self.team
        proj.pos = self.local_to_world(self.fire_pos)
        ang = self.angle
        rad = math.radians(ang)
        vel = self.proj_velocity
        vec = Vec2d(vel * math.cos(rad), vel * math.sin(rad))
        proj.velocity = vec
        proj.angle = ang
