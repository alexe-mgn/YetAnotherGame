from game_class import YTGBaseWeapon

from Engine.config import COLLISION_TYPE, CHANNEL
from Engine.geometry import Vec2d
from Engine.loading import load_model, cast_model, load_sound
from Engine.physics import BaseProjectile

import pygame
import pymunk

NAME = __name__.split('.')[-1]
MODEL = load_model('Weapons\\Models\\%s' % (NAME,))

CS = Vec2d(46, 39)


class Pivot(pymunk.PivotJoint):

    def __init__(self, a, b, *args):
        super().__init__(a, b, *args)
        self.collide_bodies = False
        # self.error_bias = pow(.2, 60)
        if a.space:
            a.space.add(self)
        elif b.space:
            b.space.add(self)


class Segment(BaseProjectile):
    RADIUS = 12
    LENGTH = 100
    max_health = 150
    lifetime = 10000
    hit_damage = 2.5

    def __init__(self):
        super().__init__()
        self.body = pymunk.Body()
        self.shape = pymunk.Segment(self.body,
                                    (-self.LENGTH / 2 + self.RADIUS, 0),
                                    (self.LENGTH / 2 - self.RADIUS, 0),
                                    self.RADIUS)
        self.shape.density = 1
        self.shape.collision_type = COLLISION_TYPE.TRACKED

    @classmethod
    def init_class(cls):
        segment_image = pygame.Surface((cls.LENGTH, cls.RADIUS * 2)).convert_alpha()
        segment_image.fill((0, 0, 0, 0))

        pygame.draw.line(segment_image, (0, 0, 0),
                         (cls.RADIUS, cls.RADIUS),
                         (cls.LENGTH - cls.RADIUS, cls.RADIUS),
                         cls.RADIUS * 2)
        pygame.draw.line(segment_image, (0, 255, 255),
                         (cls.RADIUS, cls.RADIUS),
                         (cls.LENGTH - cls.RADIUS, cls.RADIUS),
                         cls.RADIUS * 2 - 4)

        pygame.draw.circle(segment_image, (0, 255, 255), (cls.RADIUS, cls.RADIUS), cls.RADIUS)
        pygame.draw.circle(segment_image, (0, 255, 255),
                           (cls.LENGTH - cls.RADIUS, cls.RADIUS),
                           cls.RADIUS)
        cls._frames = segment_image

    def collideable(self, obj):
        return self.age > 1000 or obj.team != self.team

    def effect(self, obj, arbiter, first=True):
        if obj.team != self.team:
            obj.damage(self.hit_damage)


Segment.init_class()


class Ballast(Segment):
    max_health = 300
    size_inc = .5
    hit_damage = 10
    join_acceleration_coef = 4

    def __init__(self):
        super().__init__()
        self.body = pymunk.Body()
        self.shape = pymunk.Circle(self.body, self.RADIUS)
        self.shape.density = 4
        self.shape.collision_type = COLLISION_TYPE.TRACKED
        self.pair = None

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(
            load_model('Weapons\\Models\\energy_ballast'),
            None,
            cls.size_inc)
        cls.RADIUS = cls.size_inc * 128

    def start_step(self, upd_time):
        super().start_step(upd_time)
        if self.age > 3000 and self.pair:
            self.body.apply_force_at_world_point(
                (self.pair.position - self.position) * (self.mass * self.join_acceleration_coef),
                self.position
            )
            # self.velocity += (self.pair.position - self.position) / 10


Ballast.init_class()


class Weapon(YTGBaseWeapon):
    name = NAME
    size_inc = .5
    max_health = 60
    fire_delay = 2500
    proj_velocity = 2500
    inaccuracy = .25
    fragmentation = 14
    sound = {
        'fire': [load_sound('Weapons\\Models\\undetach', ext='wav'), {'channel': CHANNEL.NET_WEAPON}]
    }

    def __init__(self):
        super().__init__()

        self.i_body = pymunk.Body()
        self.shape = pymunk.Poly(self.body, self.POLY_SHAPE)
        self.shape.density = 1

    def force_fire(self, **kwargs):
        self.play_sound('fire')
        ca = self.angle
        da = self.inaccuracy * 360
        sa = ca - da / 2

        frag = self.fragmentation
        vel = self.proj_velocity
        segments = []

        b_a = self.spawn(Ballast)
        b_a.set_parent(self)
        b_a.angle = sa
        b_a.velocity = Vec2d.from_anglen(sa, vel)

        b_b = self.spawn(Ballast)
        b_b.set_parent(self)
        b_b.angle = sa + da
        b_b.velocity = Vec2d.from_anglen(sa + da, vel)

        b_a.pair = b_b
        b_b.pair = b_a

        w = (self.Projectile.LENGTH - self.Projectile.RADIUS) / 2

        for n in range(frag):
            proj = self.spawn_proj()

            if segments:
                Pivot(proj.body, segments[-1].body, (-w, 0), (w, 0))

            segments.append(proj)
            ang = sa + da * (n / frag)
            proj.angle = ang - 90
            proj.velocity = Vec2d.from_anglen(ang, vel * .8)

        Pivot(b_a.body, segments[0].body, (0, 0), (-w, 0))
        Pivot(b_b.body, segments[-1].body, (0, 0), (w, 0))

    @classmethod
    def init_class(cls):
        cls._frames, cls.IMAGE_SHIFT = cast_model(MODEL, CS, cls.size_inc)
        cls.precalculate_shape()
        cls.calculate_poly_shape()
        cls.Projectile = Segment
        cls.fire_pos = cls.image_to_local((170, 39))

    @classmethod
    def precalculate_shape(cls):
        radius = 40

        cls.RADIUS = radius * cls.size_inc

    @classmethod
    def calculate_poly_shape(cls):
        img_poly_left = [(0, 39), (20, 6), (158, 2)]
        poly_left = [tuple(e[n] - CS[n] for n in range(2)) for e in img_poly_left]
        poly_right = [(e[0], -e[1]) for e in poly_left[::-1]]
        cls.POLY_SHAPE = [(e[0] * cls.size_inc, e[1] * cls.size_inc) for e in poly_left + poly_right]


Weapon.init_class()
