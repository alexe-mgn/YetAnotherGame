import pygame
from Game.Character import BasePlayer, WeaponInv
from Creatures.MechZero import Creature as Body
from Components.LegsZero import Engine as Legs
from Weapons.plasma_repeater import Weapon as DefaultW
from Weapons.pulson import Weapon as Pulson


class Character(BasePlayer, Body):

    def pregenerate(self):
        self.w_inv = WeaponInv(self)
        l = Legs()
        l.max_vel = 1000
        l.add(*self.groups())
        self.mount(l, key='engine')
        for _ in range(2):
            w = DefaultW()
            w.add(self.level.phys_group)
            self.mount(w)
            self.w_inv[self.w_inv.index].append(w)
        self.w_inv[4].append(Pulson())

    def send_event(self, event):
        if not self.level.paused:
            if event.type == pygame.KEYDOWN:
                if 49 <= event.key <= 53:
                    kc = event.key - 49
                    self.w_inv.checkout(kc)
