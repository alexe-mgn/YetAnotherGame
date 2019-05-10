import pygame
import math
from geometry import Vec2d
from Game.Character import BasePlayer, WeaponInv
from Objects.MechPlayer import Creature as Body
from Components.LegsPlayer import Engine as Legs
from Weapons.plasma_repeater import Weapon as DefaultW
from config import ROLE
from Weapons.pulson import Weapon as Pulson
from Weapons.net_cannon import Weapon as Net


class Character(BasePlayer, Body):

    def pregenerate(self):
        self.max_health = 500
        self.health = self.max_health
        self.w_inv = WeaponInv(self, gui=self.gui.inventory if self.gui else None)
        l = Legs()
        l.max_vel = 400
        l.add(*self.groups())
        self.mount(l, key='engine')
        for _ in range(2):
            self.w_inv.add(DefaultW())
        for _ in range(2):
            self.w_inv.add(Pulson())
        self.w_inv.add(Net())

    def update(self):
        add = self.step_time * self.max_health * .001 / 1000
        if self.health + add <= self.max_health:
            self.health += add

    def effect(self, obj, arbiter, first=True):
        if obj.own_body() and obj.role == ROLE.WEAPON:
            self.w_inv.add(obj)

    def send_event(self, event):
        super().send_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_j:
            ind = self.w_inv.index
            for n in range(len(self.w_inv[ind])):
                w = self.w_inv.drop(ind)
                ang = math.radians(self.angle)
                vector = Vec2d(math.cos(ang), math.sin(ang))
                mv = 1000000 / w.mass
                vel = w.velocity_for_distance((self.level.mouse_absolute - self.pos).length)
                if vel > mv:
                    vel = mv
                w.pos += vector * 75
                w.velocity = vector * vel
