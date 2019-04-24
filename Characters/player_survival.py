import pygame
from Game.Character import BasePlayer, WeaponInv
from Creatures.MechZero import Creature as Body
from Components.LegsZero import Engine as Legs
from Weapons.plasma_repeater import Weapon as DefaultW
from Weapons.pulson import Weapon as Pulson


class Character(BasePlayer, Body):

    def pregenerate(self):
        self.max_health = 500
        self.health = self.max_health
        self.w_inv = WeaponInv(self)
        l = Legs()
        l.max_vel = 500
        l.add(*self.groups())
        self.mount(l, key='engine')
        for _ in range(2):
            w = DefaultW()
            w.add(self.level.phys_group)
            self.mount(w)
            self.w_inv[self.w_inv.index].append(w)
        for _ in range(2):
            self.w_inv[4].append(Pulson())

    def update(self):
        add = self.step_time * self.max_health * .01 / 1000
        if self.health + add <= self.max_health:
            self.health += add
