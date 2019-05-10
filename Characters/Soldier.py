from Objects.MechSoldier import Creature
from Game.Character import BaseEnemy
from Components.LegsSoldier import Engine as Legs
from Weapons.plasma_repeater import Weapon as DefaultW


class Character(BaseEnemy, Creature):
    score = 1

    def pregenerate(self):
        self.fire_delay = 2000
        l = Legs()
        l.add(*self.groups())
        self.mount(l, key='engine')
        w = DefaultW()
        w.add(self.level.phys_group)
        self.mount(w)
