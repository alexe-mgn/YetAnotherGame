from Engine.config import *
from Engine.geometry import Vec2d
from Engine.physics import DynamicObject, BaseCreature, BaseComponent, BaseWeapon
import math

from VFX.smoked import VideoEffect


class YTGDynamicObject(DynamicObject):
    """
    Standard game object
    """
    death_effect = VideoEffect


class YTGBaseCreature(BaseCreature):
    death_effect = VideoEffect

    def get_engines(self):
        return [e.object for e in self.mounts if e.role == ROLE.ENGINE]

    def walk(self, vec):
        engine = self.get_mount(key='engine')
        if engine:
            engine.object.walk(vec)


class YTGBaseComponent(BaseComponent):
    death_effect = VideoEffect


class BaseEngine(YTGBaseComponent):
    """
    Any movement-platform/wheels/legs
    (able of rotating independent of creature body)
    """
    draw_layer = DRAW_LAYER.CREATURE_BOTTOM
    role = ROLE.ENGINE

    engine_force = 100
    max_vel = 100
    max_fps = 10
    default_damping = None

    def __init__(self):
        super().__init__()
        self.working = False
        self._image.fps = 0
        self.parent_default_damping = 0

    def walk(self, vec):
        cv = self.velocity
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
            self.default_damping = self.damping
            self.parent_default_damping = parent.damping
            self.damping = 0
            parent.damping = 0

    def unmount(self):
        p = self._parent
        s = super().unmount()
        if s:
            self.damping = self.default_damping
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


class YTGBaseWeapon(BaseWeapon):
    death_effect = VideoEffect
