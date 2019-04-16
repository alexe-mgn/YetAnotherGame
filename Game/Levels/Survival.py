import pygame
import pymunk
from level import Level
from physics import PhysicsGroup
from Game.GUI import LevelGUI
from Game.Player import BasePlayer
from loading import load_image
from config import *


class Survival(Level):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background = pygame.transform.scale(load_image('Game\\Levels\\background.jpg', alpha=False), self.size)
        space = pymunk.Space()
        space.damping = 1
        space.gravity = [0, 0]
        group = PhysicsGroup(space)
        self.phys_group = group

        level_rect = self.get_rect()
        ps = [level_rect.topleft,
              level_rect.topright,
              level_rect.bottomright,
              level_rect.bottomleft]
        for n in range(-1, 3):
            b = pymunk.Body(body_type=pymunk.Body.STATIC)
            s = pymunk.Segment(b, ps[n], ps[n + 1], 2)
            space.add(b, s)

        from Weapons.pulson import Weapon
        w = Weapon()
        w.add(group)
        w.pos = (300, 300)
        self.w = w
        w = Weapon()
        w.add(group)
        w.pos = (300, 300)
        from Creatures.MechZero import Creature
        from Components.LegsZero import Engine

        class Player(BasePlayer, Creature):
            pass

        mc = Player(self)
        mc.add(group)
        mc.pos = (500, 500)
        mc.mount(self.w, key='weapon_left')
        #mc.mount(w, key='weapon_right')
        ls = Engine()
        ls.add(group)
        ls.pos = (300, 300)
        mc.mount(ls, key='engine')
        mc.team = TEAM.PLAYER
        self.player = mc

        for n in range(5):
            mc = Creature()
            mc.add(group)
            mc.pos = (500, 500)
            ls = Engine()
            ls.add(group)
            ls.pos = (300, 300)
            mc.mount(ls, key='engine')

        self.phys_group = group

        self.gui = LevelGUI(main=self.main)

    def draw(self, surface):
        surface.blit(
            pygame.transform.scale(
                self.background.subsurface(self.camera.get_rect().pygame),
                self.screen.size),
            (0, 0))
        super().draw(surface)
