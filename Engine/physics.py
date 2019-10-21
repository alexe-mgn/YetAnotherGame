from Engine.config import *
from Engine.geometry import Vec2d, FRect
from Engine.loading import GObject
from Engine.col_handlers import get_handler

import pygame
import pymunk

import random
import math

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


class ObjectGroup(pygame.sprite.AbstractGroup):

    def __init__(self):
        super().__init__()
        self.default_layer = 9
        self._offset = Vec2d(0, 0)
        self.sounds = []


class CameraGroup(ObjectGroup):

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
                s_img = sprite.image
                img = pygame.transform.rotozoom(s_img, -sprite.angle, zoom)

                img_size = img.get_size()
                s_pos = sprite.position
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
                to_s = snd[1].position - cam_c
                d = to_s.get_length_sqrd()
                v = SOUND_COEF / (math.sqrt(d + cam_h) + 1)
                c.set_volume(v)

        self.sounds.clear()
        self.lostsprites = []

    def que_sound(self, sound, sprite, **kwargs):
        """
        Воспроизвести звук
        :param sound: pygame.mixer.Sound
        :param sprite:
        :param kwargs: channel, loops, max_time, fade_ms
        """
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
    from Engine.debug_draw import draw_debug


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

    def __init__(self, space=None):
        super().__init__()
        self.space = space if space else pymunk.Space()

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


class BaseSprite(pygame.sprite.Sprite):
    draw_layer = DRAW_LAYER.DEFAULT
    sound = {}
    damping = None

    def __init__(self):
        """
        Necessary assignment
           - rect
           - image
        """
        super().__init__()
        self._image = None

        self._pos = Vec2d(0, 0)
        self._size = Vec2d(0, 0)
        self._angle = 0

        self.step_time = 1
        self.age = 0

        self.play_sound('creation')

    def play_sound(self, key):
        """
        Звуки хранятся в аттрибуте Sprite.sounds
        sounds = {'sound_key': [pygame.mixer.Sound, sound params {'channel', 'loops', 'max_time', 'fade_ms'}]}
        Параметры звука необязательны, можно оставить пустой словарь.
        :param key: sound key
        """
        s = self.sound.get(key, [])
        if s:
            self.group.que_sound(s[0], self, **s[1])

    def _get_space(self):
        return None

    def _set_space(self, space):
        pass

    @property
    def space(self):
        return self._get_space()

    @space.setter
    def space(self, space):
        self._set_space(space)

    def is_own_body(self):
        return True

    def _get_body(self):
        return None

    def _set_body(self, body):
        pass

    @property
    def body(self):
        return self._get_body()

    @body.setter
    def body(self, body):
        self._set_body(body)

    def local_to_world(self, pos):
        return self.position + Vec2d(pos).rotated(self.angle)

    def world_to_local(self, pos):
        return (Vec2d(pos) - self.position).rotated(-self.angle)

    def _get_mass(self):
        return 0

    def _set_mass(self, mass):
        pass

    @property
    def mass(self):
        return self._get_mass()

    @mass.setter
    def mass(self, mass):
        self._set_mass(mass)

    def _get_moment(self):
        return 0

    def _set_moment(self, moment):
        pass

    @property
    def moment(self):
        return self._get_moment()

    @moment.setter
    def moment(self, moment):
        self._set_moment(moment)

    def _get_shape(self):
        return None

    def _set_shape(self, shape):
        pass

    @property
    def shape(self):
        return self._get_shape()

    @shape.setter
    def shape(self, shape):
        self._set_shape(shape)

    def _get_shapes(self):
        return []

    @property
    def shapes(self):
        return self._get_shapes()

    def add_shape(self, shape):
        pass

    def remove_shape(self, shape):
        pass

    def _get_rect(self):
        r = FRect(*self._pos, 0, 0)
        r.inflate_ip(*self._size)
        return r

    def _set_rect(self, rect):
        self._pos = Vec2d(rect.center)
        self._size = Vec2d(rect.size)

    @property
    def rect(self):
        return self._get_rect()

    @rect.setter
    def rect(self, rect):
        self._set_rect(rect)

    def _get_bb(self):
        x, y = self._pos
        size = self._size
        hw, hh = size[0] / 2, size[1] / 2
        return pymunk.BB(x - hw, y + hh, x + hw, y - hh)

    @property
    def bb(self):
        return self._get_bb()

    def read_image(self):
        return self._image.read()

    def _get_image(self):
        return self._image.read()

    def _set_image(self, surface):
        self._image = surface

    @property
    def image(self):
        return self._get_image()

    @image.setter
    def image(self, surface):
        self._set_image(surface)

    def effect(self, obj, arbiter, first=True):
        """
        Переопределяемый.
        "Оказывает воздействие" на другой объект при столкновение.
        Пример - нанесение урона пулей.
        :param obj: PhysObject
        :param arbiter: pymunk.Arbiter
        :param first: bool - устанавливается при вызове и описывает положение объекта в arbiter (первый или второй)
        """
        pass

    def post_effect(self, obj, arbiter, first=True):
        """
        См. self.effect.
        Отличие в том, что выполняется сразу после вызова .effect обоих объектов (опять же, для обоих объектов)
        :param obj: PhysObject
        :param arbiter: pymunk.Arbiter
        :param first: bool
        """
        pass

    def post_update(self):
        pass

    def update(self):
        pass

    def start_step(self, upd_time):
        self.step_time = upd_time

    def end_step(self):
        self.age += self.step_time

    def _get_position(self):
        return self._pos

    def _set_position(self, p):
        self._pos = Vec2d(p)

    @property
    def position(self):
        return self._get_position()

    @position.setter
    def position(self, p):
        self._set_position(p)

    def _get_angle(self):
        return self._angle

    def _set_angle(self, ang):
        self._angle = ang

    @property
    def angle(self):
        return self._get_angle()

    @angle.setter
    def angle(self, ang):
        self._set_angle(ang)

    def _get_velocity(self):
        return Vec2d(0, 0)

    def _set_velocity(self, vel):
        pass

    @property
    def velocity(self):
        return self._get_velocity()

    @velocity.setter
    def velocity(self, vel):
        self._set_velocity(vel)

    def _get_angular_velocity(self):
        """
        Угловая скорость объекта
        :return: float (degrees / second)
        """
        return 0

    def _set_angular_velocity(self, ang_vel):
        pass

    @property
    def angular_velocity(self):
        return self._get_angular_velocity()

    @angular_velocity.setter
    def angular_velocity(self, ang_vel):
        self._set_angular_velocity(ang_vel)

    def collideable(self, obj):
        """
        Переопределяемый.
        Проверка столкновения с объектом.
        Возвращение False хотя бы одним приведёт к прохождению друг через друга
        :param obj: PhysObject
        :return: bool
        """
        return True

    def damage(self, val):
        """
        Переопределяемый.
        Нанести урон объекту.
        :param val:
        """
        pass

    def _get_group(self):
        return self.groups()[0]

    @property
    def group(self):
        return self._get_group()

    def stop_sounds(self, fadeout=1000):
        """
        Останавливает все издаваемые звуки с постепенным затуханием.
        :param fadeout: int (ms) ( default=1000 )
        """
        for snd in self.sound.values():
            if snd[0].get_num_channels() > 0:
                snd[0].fadeout(fadeout)

    def kill(self):
        """
        Полностью уничтожает спрайт.
        Останавливает все издаваемые звуки (в течение секунды)
        """
        self.stop_sounds()
        self.remove_pygame()

    def add_post_step_callback(self, f, fid=None):
        """
        Единоразово выполняет функцию после завершения игровой итерации pymunk.Space.step.
        Если пространство для объекта не определено, то выполняется немедленно.
        :param f:
        :param fid: уникальный id ( default=id(f) ), необходим для pymunk.space.add_post_step_callback
        """
        f()

    def remove_pygame(self):
        """
        Выполняет удаление спрайта по правилам pygame.
        """
        super().kill()

    def __bool__(self):
        return True


class StaticImage(BaseSprite):
    draw_layer = DRAW_LAYER.VFX

    def end_step(self):
        super().end_step()
        self._image.update(self.step_time)


class PhysObject(BaseSprite):
    """
    Sprite bounded to single pymunk.Body and one MAIN shape
    """

    def __init__(self):
        """
        Necessary assignment
           - rect
           - image
           - shape
        """
        super().__init__()
        self._space = None
        self._body = None
        self._shape = None

    def _get_space(self):
        """
        :return: pymunk.Space
        """
        return self._space

    def _set_space(self, space):
        """
        Установить пространство объектов pymunk.Space для self.body и всех его pymunk.Shape
        :param space: pymunk.Space
        """
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

    def is_own_body(self):
        """
        Переопределяется объектами классов Component.
        Для обычного спрайта True
        :return: bool
        """
        return True

    def _get_body(self):
        """
        "Тело" объекта. К нему привязываются pymunk.Shape частично определяющие массу, размеры, форму и т.д
        :return: pymunk.Body
        """
        return self._body

    def _set_body(self, body):
        """
        Установить тело объекта, на данный момент все его pymunk.Shape не учитываются в процессе переноса.
        :param body: pymunk.Body
        """
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
        """
        Конвертация из локальной системы координат в уровневую.
        Положение точки в локальной системе не зависит от углов наклона тела к глобальным осям.
        :param pos: (x, y)
        :return: Vec2d(x, y)
        """
        return self._body.local_to_world(pos)

    def world_to_local(self, pos):
        """
        Конвертация в локальную систему координат.
        Положение точки в локальной системе не зависит от углов наклона тела к глобальным осям.
        :param pos: (x, y)
        :return: Vec2d(x, y)
        """
        return self._body.world_to_local(pos)

    def _get_mass(self):
        return self._body.mass

    def _set_mass(self, mass):
        self._body.mass = mass

    def _get_moment(self):
        """
        Момент инерции тела.
        Единицы измерения не проверены!
        :return: float
        """
        return self._body.moment

    def _set_moment(self, m):
        """
        Установить момент инерции.
        Единицы измерения не проверены!
        :param m: float
        """
        self._body.moment = m

    def _get_shape(self):
        """
        Главный (!) shape объекта
        :return: pymunk.Shape
        """
        return self._shape

    def _set_shape(self, shape):
        """
        Главный (!) shape объекта
        :param shape: pymunk.Shape
        """
        if shape.space:
            shape.space.remove(shape)
        if shape.body is not self._body:
            shape.body = self._body
        if self._space is not None:
            if self._shape is not None:
                self._space.remove(self._shape)
            self._space.add(shape)
        self._shape = shape

    def _get_shapes(self):
        body = self._body
        return body.shapes if body is not None else []

    def add_shape(self, shape):
        """
        :param shape: pymunk.Shape
        """
        if shape.space:
            shape.space.remove(shape)
        if shape.body is not self._body:
            shape.body = self._body
        if self._space is not None:
            self._space.add(shape)

    def remove_shape(self, shape):
        """
        :param shape:
        """
        if self._space is not None:
            self._space.remove(shape)
        if shape is self._shape:
            self._shape = None
        shape.body = None

    def _get_rect(self):
        """
        Прямоугольник, описанный около объекта.
        Создаётся из pymunk.bb главного shape.
        :return:
        """
        bb = self.bb
        r = FRect(bb.left, bb.bottom, bb.right - bb.left, bb.top - bb.bottom)
        return r

    def _set_rect(self, rect):
        if self._body is not None:
            self._body.position = FRect(rect).center

    def _get_bb(self):
        """
        BoundingBox главного shape.
        :return: pymunk.BB
        """
        return self._shape.bb

    def _get_image(self):
        return self._image

    def _set_image(self, surface):
        self._image = surface

    def end_step(self):
        super().end_step()
        self.apply_damping()

    def apply_damping(self):
        """
        Имитирует трение с учётом self.damping и self.is_own_body
        """
        if self.damping and self.is_own_body():
            self.damp_velocity(self.damping)

    def damp_velocity(self, coef):
        """
        Имитирует трение умножением скорости.
        velocity = velocity * (1 - coef * time)
        :param coef: float
        """
        self.velocity *= (1 - coef * (self.step_time / 1000))

    def _get_position(self):
        return self._body.position

    def _set_position(self, p):
        self._body.position = p

    def _get_angle(self):
        """
        :return: float (degrees)
        """
        return math.degrees(self.body.angle)

    def _set_angle(self, ang):
        """
        :param ang: float (degrees)
        """
        b = self._body
        b.angle = math.radians(ang)

    def rotate_for(self, ang, speed):
        """
        WIP
        :param ang:
        :param speed:
        :return:
        """
        pass

    def _get_velocity(self):
        return self._body.velocity

    def _set_velocity(self, vel):
        self._body.velocity = (vel[0], vel[1])

    def _get_angular_velocity(self):
        """
        Угловая скорость объекта
        :return: float (degrees / second)
        """
        return math.degrees(self._body.angular_velocity)

    def _set_angular_velocity(self, ang_vel):
        self._body.angular_velocity = math.radians(ang_vel)

    def kill(self):
        """
        Полностью уничтожает спрайт.
        Останавливает все издаваемые звуки (в течение секунды)
        """
        self.remove_pymunk()
        super().kill()

    def add_post_step_callback(self, f, fid=None):
        """
        Единоразово выполняет функцию после завершения игровой итерации pymunk.Space.step.
        Если пространство для объекта не определено, то выполняется немедленно.
        :param f:
        :param fid: уникальный id ( default=id(f) ), необходим для pymunk.space.add_post_step_callback
        """
        if self._space is not None and self._space:
            self._space.add_post_step_callback(f, fid if fid is not None else id(f))
        else:
            f()

    def remove_pymunk(self):
        """
        Удаляет объект, его pymunk.Body и все pymunk.Shape
        :return:
        """
        space = self._space
        if space is not None:
            if self.shapes:
                space.remove(*self.shapes)
            if self._body is not None:
                space.remove(self._body, *self._body.constraints)
            self._space = None

    def velocity_for_distance(self, dist, time=1000):
        """
        Рассчитывает скорость,
        необходимую чтобы при текущем значении коэффициента "трения" пройти дистанцию за определённое время.
        :param dist: float - distance
        :param time: int ( ms )
        :return:
        """
        dmp = self.damping
        if dmp:
            return (2 * dist * dmp) / (math.exp(-dmp * time) + 1)
        else:
            return dist / time * 1000


class ImageHandler(PhysObject):
    """
    Sprite with GObject image in class attributes for RAM economy
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

    def _get_image(self):
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

    def damage(self, val):
        self.health -= val
        if self.health <= 0:
            self.death()

    def emit_death_effect(self):
        """
        Воспроизвести видео эффект смерти.
        """
        v = self.death_effect
        if v:
            v = v()
            v.add(*self.groups())
            v.position = self.position

    def death(self):
        """
        Уничтожает объект с воспроизведением эффекта смерти.
        ( self.emit_death_effect() + self.kill() )
        """
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

    # def _get_angle(self):
    #     return math.degrees(self.velocity.angle)


class Mount:
    """
    Mount point for components on pymunk.Body bounded sprite (creature)
    """

    def __init__(self, parent, position=None, angle=0, allowed=True, top=True):
        """
        :param parent: PhysObject
        :param position: (x, y) in local coords
        :param angle: float (degrees) angle in local coords.
        :param allowed: [config.ROLE, ...] | None | True
        :param top: bool - is object above creature or not.
        """
        self.parent = parent
        self._pos = Vec2d(0, 0) if position is None else Vec2d(position)
        self._ang = angle
        self.allowed = True if allowed is True else ([] if allowed is None else list(allowed))
        self.object = None
        self.role = None
        self.top = top

    def _get_position(self):
        return self._pos

    def _set_position(self, pos):
        if self.object is not None:
            self.object.position = pos
        self._pos = Vec2d(pos)

    @property
    def position(self):
        return self._get_position()

    @position.setter
    def position(self, pos):
        self._set_position(pos)

    def _get_angle(self):
        return self._ang

    def _set_angle(self, ang):
        if self.object is not None:
            self.object.angle = ang
        self._ang = ang

    @property
    def angle(self):
        return self._get_angle()

    @angle.setter
    def angle(self, ang):
        self._set_angle(ang)

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
        """
        Проверить, возможно ли теоретически установить объект.
        :param obj: Component
        :return: bool
        """
        return self.allowed is True or obj.role in self.allowed

    def mount_ready(self, obj):
        """
        Возможно ли прямо сейчас установить объект.
        ( self.free() * self.mountable(obj) )
        :param obj: Component
        :return: bool
        """
        return self.object is None and (self.allowed is True or obj.role in self.allowed)

    def free(self):
        """
        Проверить, свободна ли позиция.
        :return:
        """
        return self.object is None

    def __bool__(self):
        """
        :return: True if mounted else None
        """
        return self.object is not None

    def __repr__(self):
        return '{}.{}({})'.format(self.parent, self.__class__.__name__, self.object)


class BaseCreature(DynamicObject):
    """
    Объект с системой крепления компонентов и перемещения
    """
    draw_layer = DRAW_LAYER.CREATURE
    role = ROLE.CREATURE
    max_health = 100

    def __init__(self):
        super().__init__()

        self.mounts_num = 0
        self.mounts = []
        self.mounts_names = {}

    def get_mount(self, index=None, key=None, obj=None):
        """
        Получить Mount (принадлежащий объекту) по индексу, ключу или прикреплённому к нему компоненту.
        :param index: int
        OR
        :param key: str
        OR
        :param obj: Component
        :return:
        """
        if index is not None:
            return self.mounts[index]
        elif key is not None:
            return self.mounts[self.mounts_names[key]]
        elif obj is not None:
            for m in self.mounts:
                if m.object is obj:
                    return m

    def mount(self, obj, index=None, key=None):
        """
        Установить компонент.
        :param obj: Component
        :param index: int
        OR
        :param key: str
        :return: bool
        """
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
        """
        Отсоединить объект.
        :param index: int
        OR
        :param key: str
        OR
        :param obj: Component
        :return: bool
        """
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
        """
        Отсоединить все компоненты.
        """
        for n in range(len(self.mounts)):
            self.unmount(index=n)

    def mounted_objects(self):
        """
        :return: [Component, ...]
        """
        return [e.object for e in self.mounts if e]

    def init_mounts(self, *mounts):
        """
        Инициализирует систему крепления компонентов
        :param mounts: [Mount, mount_name] | Mount, ...
        :return:
        """
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
        """
        Получить все установленные объекты с role == config.ROLE.WEAPON
        :return: [BaseWeapon, ...]
        """
        return [e.object for e in self.mounts if e.role == ROLE.WEAPON]

    def free_weapon(self):
        """
        Возвращает пустой Mount для оружия.
        :return:
        """
        for i in self.mounts:
            if i.role == ROLE.WEAPON and i.free():
                return i

    def shot(self, **kwargs):
        """
        Выстрел из всех оружий.
        :param kwargs:
        """
        for i in self.get_weapons():
            i.shot(**kwargs)

    def kill(self):
        self.unmount_all()
        super().kill()


class BaseComponent(DynamicObject):
    """
    Объект с возможностью установки на Mount.
    Дополнительно преобретает аттрибут self.i_body,
    который характеризуют его в отсоединённом от Mount состояния.
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
            pos = self.position
            ang = self.angle
            self._parent = None
            if self._space is not None:
                self._space.add(self._i_body)
            self.body = self._i_body
            self.set_local_placement((0, 0), 0)
            self.position = pos
            self.angle = ang

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    def _set_space(self, space):
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
        """
        Начальная форма объекта. Текущая обычно развёрнута с учётом наклона Mount.
        :return:
        """
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

    def _get_shapes(self):
        shape = self.shape
        return [shape] if shape is not None else []

    def is_own_body(self):
        return self.body is self.i_body

    def _set_body(self, body):
        self.space = None
        self._body = None
        if self._i_shape is not None:
            self._shape.body = body
        self.space = body.space
        self._body = body

    def _get_i_body(self):
        """
        Собственное тело компонента. Когда установлен оно уничтожается, а при отсоединении создаётся.
        :return: pymunk.Body
        """
        return self._i_body

    def _set_i_body(self, body):
        if self.is_own_body():
            self.body = body
        if self._i_body is not None:
            self._i_body.sprite = None
        self._i_body = body
        body.sprite = self

    @property
    def i_body(self):
        return self._get_i_body()

    @i_body.setter
    def i_body(self, body):
        self._set_i_body(body)

    def preview(self, size):
        """
        Возвращает preview для инвентаря.
        :param size: (width, height)
        :return: pygame.Surface
        """
        i_img = self._image[0]
        img_b_rect = i_img.get_bounding_rect()
        img = i_img.subsurface(img_b_rect)
        r = FRect(img_b_rect).fit(FRect(0, 0, *size))
        return pygame.transform.scale(img, [int(e) for e in r.size])

    def update_local_placement(self):
        """
        Устанавливает форму объекта в соответсвтие с локальным положением
        :return:
        """
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

    def _get_local_pos(self):
        return self._pos

    def _set_local_pos(self, pos):
        self._pos = Vec2d(pos)
        self.update_local_placement()

    @property
    def local_pos(self):
        return self._get_local_pos()

    @local_pos.setter
    def local_pos(self, pos):
        self._set_local_pos(pos)

    def _get_local_angle(self):
        return self._ang

    def _set_local_angle(self, ang):
        self._ang = ang
        self.update_local_placement()

    @property
    def local_angle(self):
        return self._get_local_angle()

    @local_angle.setter
    def local_angle(self, ang):
        self._set_local_angle(ang)

    def _get_position(self):
        return self._body.local_to_world(self._pos)

    def _set_position(self, p):
        if not self.mounted():
            self._body.position = p

    def _get_angle(self):
        return math.degrees(self._body.angle) + self._ang

    def _set_angle(self, ang):
        if self.mounted():
            self._ang = ang - math.degrees(self._body.angle)
        else:
            self._body.angle = math.radians(ang)
        self.update_local_placement()

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
        obj.position = self.local_to_world(self.fire_pos)
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
