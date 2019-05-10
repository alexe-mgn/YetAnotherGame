from Objects.MechZero import Creature
from Game.Character import BaseEnemy
from Components.LegsZero import Engine as Legs
from Weapons.pulson import Weapon as DefaultW


class Character(BaseEnemy, Creature):
    score = 5

    def pregenerate(self):
        self.fire_delay = 3000
        l = Legs()
        l.add(*self.groups())
        self.mount(l, key='engine')
        w = DefaultW()
        w.add(self.level.phys_group)
        self.mount(w)
