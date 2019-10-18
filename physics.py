import random

import pygame
import pymunk

from config import ROLE, TEAM, MAT_TYPE, COLLISION_TYPE, DRAW_LAYER
from geometry import Vec2d, FRect
from config import *
from col_handlers import get_handler
import math

from loading import GObject

pygame.mixer.set_reserved(len(CHANNEL.values()))


def collide_case(a, b):
    """
    Стандартная функция проверки колизии двух спрайтов.
    """
    ta, tb = getattr(a, 'team', TEAM.DEFAULT), getattr(b, 'team', TEAM.DEFAULT)
    ma, mb = getattr(a, 'mat', MAT_TYPE.MATERIAL), getattr(b, 'mat', MAT_TYPE.MATERIAL)
    if ma == mb == MAT_TYPE.ENERGY:
        return False
    if ta != tb:
        return True
    elif ta == TEAM.DEFAULT:
        return True
    else:
        return False


class CameraGroup(pygame.sprite.AbstractGroup):
    """
    Layered sprite group with camera-handling draw method.
    """

    def __init__(self):
        super().__init__()
        self.default_layer = 9
        self._offset = Vec2d(0, 0)
        self.sounds = []

    def layer_sorted(self):
        return sorted(self.sprites(), key=lambda e: getattr(e, 'draw_layer', self.default_layer))

    def draw(self, surface, camera):
        cam_rect = camera.get_rect()
        cam_bb = pymunk.BB(cam_rect.left, cam_rect.top, cam_rect.right, cam_rect.bottom)
        cam_tl = Vec2d(cam_rect.topleft)
        cam_offset = Vec2d(self.draw_offset)
        zoom = camera.get_current_zoom()

        blit = surface.blit
        sprite_dict = self.spritedict

        for sprite in self.layer_sorted():
            if sprite.bb.intersects(cam_bb):
                s_img = sprite.read_image()
                img = pygame.transform.rotozoom(s_img, -sprite.angle, zoom)

                img_size = img.get_size()
                s_pos = sprite.pos
                sc = (
                    int(cam_offset[0] + (s_pos[0] - cam_tl[0]) * zoom - img_size[0] / 2),
                    int(cam_offset[1] + (s_pos[1] - cam_tl[1]) * zoom - img_size[1] / 2)
                )
                sprite_dict[sprite] = blit(img, sc)

        cam_c = Vec2d(cam_rect.center)
        cam_h = (CAMERA_SOUND_HEIGHT / zoom) ** 2
        for snd in self.sounds:
            sound = snd[0]
            kwargs = snd[2]
            c = kwargs.get('channel', None)
            if c is not None:
                c = pygame.mixer.Channel(c)
                c.play(sound)
            else:
                c = sound.play(kwargs.get('loops', 0), kwargs.get('max_time', 0), kwargs.get('fade_ms', 0))
            if c is not None:
                to_s = snd[1].pos - cam_c
                d = to_s.get_length_sqrd()
                v = SOUND_COEF / (math.sqrt(d + cam_h) + 1)
                c.set_volume(v)

        self.sounds.clear()
        self.lostsprites = []

    def que_sound(self, sound, sprite, **kwargs):
        self.sounds.append([sound, sprite, kwargs])

    @property
    def draw_offset(self):
        return self._offset

    @draw_offset.setter
    def draw_offset(self, vec):
        self._offset = Vec2d(vec)


if DEBUG.COLLISION:
    import functools
    import types
    from debug_draw import draw_debug


    def copy_func(f):
        """Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)"""
        g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
                               argdefs=f.__defaults__,
                               closure=f.__closure__)
        g = functools.update_wrapper(g, f)
        g.__kwdefaults__ = f.__kwdefaults__
        return g


    old = copy_func(CameraGroup.draw)


    def draw(self, surface, camera):
        old(self, surface, camera)
        draw_debug(surface, camera, self.sprites())


    CameraGroup.draw = draw


class PhysicsGroup(CameraGroup):
    """
    Sprite group handling pymunk objects.
    """

    def __init__(self, space):
        super().__init__()
        self.space = space

    def update(self, upd_time):
        sprites = self.sprites()
        for s in sprites:
            s.start_step(upd_time)
            s.update()
        self._space.step(upd_time / 1000)
        for s in sprites:
            if s:
                s.post_update()
                s.end_step()

    def remove_internal(self, sprite):
        super().remove_internal(sprite)
        sprite.space = None

    def add_internal(self, sprite):
        super().add_internal(sprite)
        sprite.space = self._space

    @property
    def space(self):
        return self._space

    @space.setter
    def space(self, space):
        for s in self.sprites():
            s.space = space
        self._space = space
        hs = []
        for c in COLLISION_TYPE.values():
            if c not in hs:
                ch = get_handler(c)
                if ch is not None:
                    dh = space.add_wildcard_collision_handler(c)
                    for i in ['begin', 'pre_solve', 'post_solve', 'separate']:
                        if hasattr(ch, i):
                            setattr(dh, i, getattr(ch, i))
                hs.append(c)


class StaticImage(pygame.sprite.Sprite):
    """
    Non-physical sprite with only image, but still usable by PhysicsGroup.
    """

    draw_layer = DRAW_LAYER.VFX
    sound = {}

    def __init__(self):
        """
        Necessary assignment
           - rect
           - image
        """
        self._pos = Vec2d(0, 0)
        self._size = Vec2d(0, 0)
        self._angle = 0

        self._image = None

        self.damping = 0
        self.step_time = 1
        super().__init__()
        self.play_sound('creation')

    def play_sound(self, key):
        s = self.sound.get(key, [])
        if s:
            self.group.que_sound(s[0], self, **s[1])

    @property
    def space(self):
        return None

    @space.setter
    def space(self, space):
        pass

    def own_body(self):
        return True

    @property
    def body(self):
        return None

    @body.setter
    def body(self, body):
        pass

    def local_to_world(self, pos):
        return self.pos + Vec2d(pos).rotated(self.angle)

    def world_to_local(self, pos):
        return (Vec2d(pos) - self.pos).rotated(-self.angle)

    @property
    def mass(self):
        return 0

    @mass.setter
    def mass(self, m):
        pass

    @property
    def moment(self):
        return 0

    @moment.setter
    def moment(self, m):
        pass

    @property
    def shape(self):
        return None

    @shape.setter
    def shape(self, shape):
        pass

    @property
    def shapes(self):
        return []

    def add_shape(self, shape):
        pass

    def remove_shape(self, shape):
        pass

    @property
    def rect(self):
        r = FRect(*self._pos, 0, 0)
        r.inflate_ip(*self._size)
        return r

    @rect.setter
    def rect(self, rect):
        self._pos = Vec2d(rect.center)
        self._size = Vec2d(rect.size)

    @property
    def bb(self):
        x, y = self._pos
        size = self._size
        hw, hh = size[0] / 2, size[1] / 2
        return pymunk.BB(x - hw, y + hh, x + hw, y - hh)

    @property
    def image(self):
        return self._image.read()

    # THIS MUST be used for drawing, not .image
    def read_image(self):
        return self.image

    @image.setter
    def image(self, surf):
        self._image = surf

    def effect(self, obj, arbiter, first=True):
        pass

    def post_update(self):
        pass

    def update(self):
        pass

    def start_step(self, upd_time):
        self.step_time = upd_time

    def end_step(self):
        self._image.update(self.step_time)

    def _get_pos(self):
        return self._pos

    def _set_pos(self, p):
        self._pos = Vec2d(p)

    pos, center = property(_get_pos, _set_pos), property(_get_pos, _set_pos)

    def _get_angle(self):
        return self._angle

    def _set_angle(self, ang):
        self._angle = ang

    ang, angle = property(_get_angle, _set_angle), property(_get_angle, _set_angle)

    def _get_velocity(self):
        return Vec2d(0, 0)

    def _set_velocity(self, vel):
        pass

    vel, velocity = property(_get_velocity, _set_velocity), property(_get_velocity, _set_velocity)

    def collideable(self, obj):
        return False

    def damage(self, val):
        pass

    @property
    def group(self):
        return self.groups()[0]

    def kill(self):
        for snd in self.sound.values():
            if snd[0].get_num_channels() > 0:
                snd[0].fadeout(1000)
        super().kill()

    def __bool__(self):
        return True


class PhysObject(pygame.sprite.Sprite):
    """
    Sprite bounded to single pymunk.Body and one MAIN shape
    """
    draw_layer = DRAW_LAYER.DEFAULT
    damping = None
    sound = {}

    def __init__(self):
        """
        Necessary assignment
           - rect
           - image
           - shape
        """
        self._image = None
        self._space = None
        self._body = None
        self._shape = None

        self.step_time = 1
        self.age = 0
        super().__init__()
        self.play_sound('creation')

    def play_sound(self, key):
        s = self.sound.get(key, [])
        if s:
            self.group.que_sound(s[0], self, **s[1])

    @property
    def space(self):
        return self._space

    @space.setter
    def space(self, space):
        shapes = self.shapes
        if self._space is not None:
            if shapes:
                self._space.remove(*shapes)
            if self._body is not None:
                self._space.remove(self._body)
        self._space = space
        if space is not None:
            if self._body is not None:
                space.add(self._body)
            if shapes:
                space.add(shapes)

    def own_body(self):
        return True

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, body):
        # shapes !!!
        if self._space is not None:
            if self._body is not None:
                self._body.sprite = None
                self._space.remove(self._body)
            self._space.add(body)
        self._body = body
        if body is not None:
            body.sprite = self

    def local_to_world(self, pos):
        return self._body.local_to_world(pos)

    def world_to_local(self, pos):
        return self._body.world_to_local(pos)

    @property
    def mass(self):
        return self._body.mass

    @mass.setter
    def mass(self, m):
        self._body.mass = m

    @property
    def moment(self):
        return self._body.moment

    @moment.setter
    def moment(self, m):
        self._body.moment = m

    def _get_shape(self):
        return self._shape

    def _set_shape(self, shape):
        if shape.space:
            shape.space.remove(shape)
        if shape.body is not self._body:
            shape.body = self._body
        if self._space is not None:
            if self._shape is not None:
                self._space.remove(self._shape)
            self._space.add(shape)
        self._shape = shape

    shape = property(_get_shape, _set_shape)

    @property
    def shapes(self):
        body = self._body
        return body.shapes if body is not None else []

    def add_shape(self, shape):
        if shape.space:
            shape.space.remove(shape)
        if shape.body is not self._body:
            shape.body = self._body
        if self._space is not None:
            self._space.add(shape)

    def remove_shape(self, shape):
        if self._space is not None:
            self._space.remove(shape)
        if shape is self._shape:
            self._shape = None
        shape.body = None

    @property
    def rect(self):
        bb = self.bb
        r = FRect(bb.left, bb.bottom, bb.right - bb.left, bb.top - bb.bottom)
        return r

    @rect.setter
    def rect(self, rect):
        if self._body is not None:
            self._body.position = FRect(rect).center

    @property
    def bb(self):
        return self._shape.bb

    @property
    def image(self):
        return self._image

    # THIS MUST be used for drawing, not .image
    def read_image(self):
        return self.image

    @image.setter
    def image(self, surf):
        self._image = surf

    def effect(self, obj, arbiter, first=True):
        pass

    def post_effect(self, obj, arbiter, first=True):
        pass

    def post_update(self):
        pass

    def update(self):
        pass

    def start_step(self, upd_time):
        self.step_time = upd_time

    def end_step(self):
        self.age += self.step_time
        self.apply_damping()

    def apply_damping(self):
        if self.damping and self.own_body():
            self.damp_velocity(self.damping)

    def damp_velocity(self, coef):
        self.velocity *= (1 - coef * (self.step_time / 1000))

    def _get_pos(self):
        return self._body.position

    def _set_pos(self, p):
        self.body.position = p

    pos, position, center = property(_get_pos, _set_pos), property(_get_pos, _set_pos), property(_get_pos, _set_pos)

    def _get_angle(self):
        return math.degrees(self.body.angle)

    def _set_angle(self, ang):
        b = self._body
        b.angle = math.radians(ang)

    ang, angle = property(_get_angle, _set_angle), property(_get_angle, _set_angle)

    def _get_velocity(self):
        return self._body.velocity

    def _set_velocity(self, vel):
        self._body.velocity = (vel[0], vel[1])

    vel, velocity = property(_get_velocity, _set_velocity), property(_get_velocity, _set_velocity)

    def kill(self):
        self.remove_pymunk()
        # self._shape = None
        # self._body = None
        self.stop_sounds()
        self.remove_pygame()

    def add_post_step_callback(self, f, fid=None):
        if self._space is not None and self._space:
            self._space.add_post_step_callback(f, fid if fid is not None else id(f))
        else:
            f()

    def remove_pygame(self):
        super().kill()

    def remove_pymunk(self):
        space = self._space
        if space is not None:
            if self.shapes:
                space.remove(*self.shapes)
            if self._body is not None:
                space.remove(self._body, *self._body.constraints)
            self._space = None

    def stop_sounds(self):
        for snd in self.sound.values():
            if snd[0].get_num_channels() > 0:
                snd[0].fadeout(1000)

    def collideable(self, obj):
        return True

    def damage(self, val):
        pass

    @property
    def group(self):
        return self.groups()[0]

    def velocity_for_distance(self, dist, time=1000):
        dmp = self.damping
        if dmp:
            return (2 * dist * dmp) / (math.exp(-dmp * time) + 1)
        else:
            return dist / time * 1000


class ImageHandler(PhysObject):
    """
    Sprite for storing image in class attributes for RAM economy
    """
    size_inc = 1
    _frames = []
    IMAGE_SHIFT = Vec2d(0, 0)

    def __init__(self, obj=None):
        super().__init__()
        if obj is None:
            self._image = GObject(self._frames)
        else:
            self._image = GObject(obj)

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
    """
    Standard game object
    """
    role = ROLE.OBJECT
    team = TEAM.DEFAULT
    mat = MAT_TYPE.MATERIAL
    name = 'None'
    max_health = 100
    death_effect = None

    def __init__(self):
        super().__init__()
        self.health = self.max_health

    def _get_shape(self):
        return super()._get_shape()

    def _set_shape(self, shape):
        super()._set_shape(shape)
        shape.collision_type = COLLISION_TYPE.TRACKED

    shape = property(_get_shape, _set_shape)

    def damage(self, val):
        self.health -= val
        if self.health <= 0:
            self.death()

    def emit_death_effect(self):
        v = self.death_effect
        if v:
            v = v()
            v.add(*self.groups())
            v.pos = self.pos

    def death(self):
        self.emit_death_effect()
        self.kill()


class BaseProjectile(DynamicObject):
    draw_layer = DRAW_LAYER.PROJECTILE
    role = ROLE.PROJECTILE
    lifetime = 1000
    hit_damage = 10

    def __init__(self):
        super().__init__()
        self.life_left = self.lifetime
        self.parent = None
        self.timeout = False

    # BODY SHAPES !!!

    def set_parent(self, parent):
        self.parent = parent
        self.team = parent.team

    def collideable(self, obj):
        return obj is not self.parent and collide_case(self, obj)

    def effect(self, obj, arbiter, first=True):
        obj.damage(self.hit_damage)

    def end_step(self):
        super().end_step()
        self.life_left -= self.step_time
        if self.life_left <= 0:
            if not self.timeout:
                self.death()
            self.timeout = True
        else:
            self.timeout = False

    def _get_angle(self):
        return math.degrees(self.velocity.angle)


class Mount:
    """
    Mount point for components on pymunk.Body bounded sprite (creature)
    """

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
            obj.team = self.parent.team
            obj.draw_layer = DRAW_LAYER.CREATURE_TOP if self.top else DRAW_LAYER.CREATURE_BOTTOM
            return True
        else:
            return False

    def unmount(self):
        if self.object is not None:
            self.object.unmount()
            del self.object.draw_layer
            del self.object.team
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


class BaseCreature(DynamicObject):
    draw_layer = DRAW_LAYER.CREATURE
    role = ROLE.CREATURE
    max_health = 100

    def __init__(self):
        super().__init__()

        self.mounts_num = 0
        self.mounts = []
        self.mounts_names = {}

    def get_mount(self, index=None, key=None, obj=None):
        if index is not None:
            return self.mounts[index]
        elif key is not None:
            return self.mounts[self.mounts_names[key]]
        elif obj is not None:
            for m in self.mounts:
                if m.object is obj:
                    return m

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

    def unmount(self, index=None, key=None, obj=None):
        m = self.get_mount(index, key, obj)
        if m is not None:
            o = m.object
            s = m.unmount()
            if s:
                o.team = TEAM.DEFAULT
                o.deactivate()
            return s
        return False

    def unmount_all(self):
        for n in range(len(self.mounts)):
            self.unmount(index=n)

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
        self.mounts_num = len(self.mounts)

    def get_weapons(self):
        return [e.object for e in self.mounts if e.role == ROLE.WEAPON]

    def free_weapon(self):
        for i in self.mounts:
            if i.role == ROLE.WEAPON and i.free():
                return i

    def shot(self, **kwargs):
        for i in self.get_weapons():
            i.shot(**kwargs)

    def kill(self):
        self.unmount_all()
        super().kill()


class BaseComponent(DynamicObject):
    """
    Mountable physical object
    """
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

    def _get_shape(self):
        return super()._get_shape()

    def _set_shape(self, shape):
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
        shape.collision_type = COLLISION_TYPE.TRACKED
        self.update_local_placement()

    shape = property(_get_shape, _set_shape)

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

    def preview(self, size):
        i_img = self._image[0]
        img_b_rect = i_img.get_bounding_rect()
        img = i_img.subsurface(img_b_rect)
        r = FRect(img_b_rect).fit(FRect(0, 0, *size))
        return pygame.transform.scale(img, [int(e) for e in r.size])

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
            self._body.position = p

    pos, position, center = property(_get_pos, _set_pos), property(_get_pos, _set_pos), property(_get_pos, _set_pos)

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


class BaseWeapon(BaseComponent):
    draw_layer = DRAW_LAYER.WEAPON
    role = ROLE.WEAPON
    fire_pos = Vec2d(0, 0)
    proj_velocity = 1000
    fire_delay = 1000
    inaccuracy = .02
    Projectile = None

    def __init__(self):
        super().__init__()
        self.recharge = 0

    def end_step(self):
        super().end_step()
        if self.recharge > 0:
            self.recharge -= self.step_time

    def shot(self, **kwargs):
        if self.recharge <= 0:
            self.force_fire(**kwargs)
            self.recharge = self.fire_delay

    def spawn(self, cls):
        obj = cls()
        obj.add(*self.groups())
        obj.pos = self.local_to_world(self.fire_pos)
        return obj

    def spawn_proj(self):
        if self.Projectile:
            proj = self.spawn(self.Projectile)
            proj.set_parent(self)
            return proj

    def miss_angle(self):
        return self.angle + 360 * (random.random() - .5) * self.inaccuracy

    def force_fire(self, **kwargs):
        self.play_sound('fire')
        proj = self.spawn_proj()
        ang = self.miss_angle()
        rad = math.radians(ang)
        vel = self.proj_velocity
        vec = Vec2d(vel * math.cos(rad), vel * math.sin(rad))
        proj.velocity = vec
        proj.angle = ang