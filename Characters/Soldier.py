from Creatures.MechZero import Creature
from Game.Character import BaseEnemy
from Weapons.plasma_repeater import Weapon


class Character(BaseEnemy, Creature):

    def __init__(self, level):
        super().__init__(level)

