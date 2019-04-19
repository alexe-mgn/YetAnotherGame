import pygame
from geometry import Vec2d
from game_class import BaseCreature
from config import *


class WeaponInv:

    def __init__(self, parent):
        self.parent = parent
        self.weapons = [[], [], [], [], []]
        self._ind = 0

    def checkout(self, ind):
        parent = self.parent
        cw = self.weapons[self._ind]
        for n, m in enumerate(parent.mounts):
            obj = m.object
            print(obj, cw)
            if obj is not None and obj in cw:
                if parent.unmount(index=n):
                    print('unm')
                    obj.remove(obj.groups())
        for obj in self.weapons[ind]:
            if parent.mount(obj):
                obj.add(parent.groups())
        self._ind = ind

    def __len__(self):
        return len(self.weapons)

    def __getitem__(self, ind):
        return self.weapons[ind]

    @property
    def index(self):
        return self._ind

    @index.setter
    def index(self, n):
        if n != self.index and 0 <= n <= len(self):
            self.checkout(n)


class BasePlayer(BaseCreature):
    team = TEAM.PLAYER

    def __init__(self, level):
        super().__init__()
        self.level = level
        if getattr(level, 'phys_group', None) is not None:
            self.add(level.phys_group)
        self.pregenerate()

    def pregenerate(self):
        pass

    def send_event(self, event):
        pass

    def handle_keys(self):
        if not self.level.paused:
            pressed = pygame.key.get_pressed()
            self.walk((
                int(pressed[pygame.K_d]) - int(pressed[pygame.K_a]),
                int(pressed[pygame.K_s]) - int(pressed[pygame.K_w])
            ))
            if pygame.mouse.get_pressed()[0]:
                self.shot()

    def update(self):
        if not self.level.paused:
            self.angle = (self.level.mouse_absolute - self.pos).angle

    def death(self):
        super().death()
        # self.level.end_game()


class BaseEnemy(BaseCreature):
    team = TEAM.ENEMY

    def __init__(self, level):
        super().__init__()
        self.level = level
        if getattr(level, 'phys_group', None) is not None:
            self.add(level.phys_group)
        self.target = self.level.player
        self.fire_delay = 1000
        self.fire_after = self.fire_delay
        self.pregenerate()

    def pregenerate(self):
        pass

    def update(self):
        if not self.level.paused and self.target is not None:
            t_pos = Vec2d(self.target.pos)
            to_t = t_pos - self.pos
            self.walk(to_t)
            self.angle = to_t.angle
            self.handle_fire()

    def handle_fire(self):
        if self.fire_after <= 0:
            self.shot()
            self.fire_after = self.fire_delay
        else:
            self.fire_after -= self.step_time