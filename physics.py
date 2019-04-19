import pygame
from geometry import Vec2d, FRect
from config import *
from col_handlers import get_handler
import math


class CameraGroup(pygame.sprite.AbstractGroup):

    def __init__(self):
        super().__init__()
        self.default_layer = 9
        self._offset = Vec2d(0, 0)

    def layer_sorted(self):
        return sorted(self.sprites(), key=lambda e: getattr(e, 'draw_layer', self.default_layer))

    def draw(self, surface, camera):
        cam_rect = camera.get_rect()
        cam_tl = Vec2d(cam_rect.topleft)
        cam_offset = self.draw_offset
        zoom = camera.get_current_zoom()
        blit = surface.blit
        for sprite in self.layer_sorted():
            if sprite.rect.colliderect(cam_rect):
                s_img = sprite.read_image()
                s_size = Vec2d(s_img.get_size())
                tl = ((-s_size / 2 - cam_tl + sprite.pos) * zoom).int()
                # tl = [int((e[1] - e[2] / 2 - e[0]) * zoom) for e in zip(cam_tl, sprite.pos, s_size)]
                self.spritedict[sprite] = blit(
                    pygame.transform.scale(s_img, (s_size * zoom).int()), tl + cam_offset)
        self.lostsprites = []

    @property
    def draw_offset(self):
        return self._offset

    @draw_offset.setter
    def draw_offset(self, vec):
        self._offset = Vec2d(vec)


class PhysicsGroup(CameraGroup):

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
    draw_layer = DRAW_LAYER.VFX

    def __init__(self):
        """
        Necessary assignment
           - rect
           - image
           - shape
        """
        self._rect = None
        self._angle = 0

        self._image = None

        self.damping = 0
        self.height = 0
        self.step_time = 1
        super().__init__()

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
        return self._rect

    @rect.setter
    def rect(self, rect):
        self._rect = FRect(rect)

    @property
    def image(self):
        return self._image.read()

    # THIS MUST be used for drawing, not .image
    def read_image(self):
        return pygame.transform.rotate(self.image, -self.angle)

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

    def apply_rect(self):
        pass

    def _get_pos(self):
        return self._rect.center

    def _set_pos(self, p):
        self._rect.center = p

    pos, center = property(_get_pos, _set_pos), property(_get_pos, _set_pos)

    def _get_angle(self):
        return self._angle

    def _set_angle(self, ang):
        self._angle = ang

    ang, angle = property(_get_angle, _set_angle), property(_get_angle, _set_angle)

    def _get_velocity(self):
        return (0, 0)

    def _set_velocity(self, vel):
        pass

    vel, velocity = property(_get_velocity, _set_velocity), property(_get_velocity, _set_velocity)

    def collideable(self, obj):
        return False

    def damage(self, val):
        pass

    def __bool__(self):
        return True


class PhysObject(pygame.sprite.Sprite):
    draw_layer = DRAW_LAYER.DEFAULT

    def __init__(self):
        """
        Necessary assignment
           - rect
           - image
           - shape
        """
        self._rect = None

        self._image = None
        self._space = None
        self._body = None
        self._shape = None

        self.damping = 0
        self.height = 0
        self.step_time = 1
        super().__init__()

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
        if self._rect is not None:
            self._rect.center = body.position

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
        return self._rect

    @rect.setter
    def rect(self, rect):
        self._rect = FRect(rect)
        if self._body is not None:
            self._body.position = self._rect.center

    @property
    def image(self):
        return self._image

    # THIS MUST be used for drawing, not .image
    def read_image(self):
        return pygame.transform.rotate(self.image, -self.angle)

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
        self.apply_damping()
        self.apply_rect()

    def apply_rect(self):
        self._rect.center = self.pos

    def apply_damping(self):
        if self.height <= 0 and self.damping:
            self.velocity *= (1 - self.damping)

    def _get_pos(self):
        return self._body.position

    def _set_pos(self, p):
        self._rect.center = p
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
        space = self._space
        if space is not None:
            if self.shapes:
                space.remove(*self.shapes)
            if self._body is not None:
                space.remove(self._body)
            self._space = None
        # self._shape = None
        # self._body = None
        super().kill()

    def collideable(self, obj):
        return True

    def damage(self, val):
        pass

    def __bool__(self):
        return bool(self.groups())
