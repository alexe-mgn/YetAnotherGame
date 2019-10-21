from Engine.config import TEAM
from Engine.geometry import Vec2d
from game_class import YTGBaseCreature

import pygame


class WeaponInv:

    def __init__(self, parent, gui=None):
        self.parent = parent
        self.gui = gui
        self.weapons = [[], [], [], [], []]
        self._ind = 0

    def checkout(self, ind):
        if ind != self.index and 0 <= ind <= len(self):
            parent = self.parent
            cw = self.weapons[self._ind]
            for n, m in enumerate(parent.mounts):
                obj = m.object
                if obj is not None and obj in cw:
                    if parent.unmount(index=n):
                        obj.remove(obj.groups())
            for obj in self.weapons[ind]:
                if parent.mount(obj):
                    obj.add(parent.groups())
            self._ind = ind

    def slot_for(self, w):
        free = None
        mn = 0
        for m in self.parent.mounts:
            if m.mountable(w):
                mn += 1
        for n, s in enumerate(self.weapons):
            if s:
                if s[0].name == w.name:
                    if len(s) < mn:
                        return n
                    else:
                        return None
            elif free is None:
                free = n
        return free

    def add(self, w):
        slot = self.slot_for(w)
        if slot is not None and w not in self.weapons[slot]:
            self.weapons[slot].append(w)
            w.remove(w.groups())
            if slot == self._ind:
                if self.parent.mount(w):
                    w.add(self.parent.groups())
            if self.gui:
                self.gui.recalculate_icons()

    def drop(self, ind, w_ind=-1):
        w = self.weapons[ind].pop(w_ind)
        if ind == self._ind:
            self.parent.unmount(obj=w)
        w.add(self.parent.groups())
        if self.gui:
            self.gui.recalculate_icons()
        return w

    def __len__(self):
        return len(self.weapons)

    def __getitem__(self, ind):
        return self.weapons[ind]

    def __iter__(self):
        return iter(self.weapons)

    @property
    def index(self):
        return self._ind

    @index.setter
    def index(self, n):
        self.checkout(n)


class BasePlayer(YTGBaseCreature):
    team = TEAM.PLAYER
    score = 0

    def __init__(self, level, gui=None):
        super().__init__()
        self.level = level
        self.gui = gui
        if getattr(level, 'add', None) is not None:
            level.add(self)
        self.pregenerate()

    def pregenerate(self):
        pass

    def send_event(self, event):
        pass

    def handle_keys(self):
        pressed = pygame.key.get_pressed()
        self.walk((
            int(pressed[pygame.K_d]) - int(pressed[pygame.K_a]),
            int(pressed[pygame.K_s]) - int(pressed[pygame.K_w])
        ))
        if pygame.mouse.get_pressed()[0]:
            self.shot(target=self.level.mouse_world,
                      target_function=lambda level=self.level: level.mouse_world)

    def start_step(self, upd_time):
        super().start_step(upd_time)
        if not self.level.paused:
            self.angle = (self.level.mouse_world - self.position).angle
            self.angular_velocity = 0

    def death(self):
        super().death()
        self.level.end_game()


class BaseEnemy(YTGBaseCreature):
    team = TEAM.ENEMY
    score = 0

    def __init__(self, level):
        super().__init__()
        self.level = level
        if getattr(level, 'add', None) is not None:
            level.add(self)
        self.target = self.level.player
        self.fire_delay = 1000
        self.fire_after = self.fire_delay
        self.pregenerate()

    def pregenerate(self):
        pass

    def update(self):
        if self.target is None or not self.target.alive():
            self.target = self.level.player
        if not self.level.paused and self.target is not None:
            t_pos = Vec2d(self.target.position)
            to_t = t_pos - self.position
            self.walk(to_t)
            self.angle = to_t.angle
            self.handle_fire()

    def handle_fire(self):
        if self.fire_after <= 0:
            self.shot(target=self.target.position)
            self.fire_after = self.fire_delay
        else:
            self.fire_after -= self.step_time

    def death(self):
        super().death()
        self.level.add_score(self.score)
