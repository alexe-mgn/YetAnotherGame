import pygame
import pymunk
from geometry import Vec2d, FRect
from config import *
from col_handlers import get_handler
import math

pygame.mixer.set_reserved(len(CHANNEL.values()))


def collide_case(a, b):
    """
    Standard "check collideable" function for two sprites.
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
            s.pre_update()
        self._space.step(upd_time / 1000)
        for s in sprites:
            if s:
                s.update()
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

    def pre_update(self):
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

    def pre_update(self):
        pass

    def update(self):
        pass

    def start_step(self, upd_time):
        self.step_time = upd_time

    def end_step(self):
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

    pos, center = property(_get_pos, _set_pos), property(_get_pos, _set_pos)

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
                space.remove(self._body)
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
