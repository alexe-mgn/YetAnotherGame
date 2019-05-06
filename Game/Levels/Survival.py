import pygame
import pymunk

from level import Level, Event
from physics import PhysicsGroup
from Game.GUI import LevelGUI
from loading import load_image
from config import *

from VFX.quantum_string import VideoEffect as SpawnCircle
from Characters.Soldier import Character as Soldier
from Characters.Zero import Character as Zero
from level import EventSystem

import random


class SpawnEvent(Event):

    def __init__(self, es):
        super().__init__(es)
        self.lu = 0
        self.characters = [
            [Soldier, .8, 0],
            [Zero, .4, 0]
        ]

    def update(self):
        if not self.level.paused:
            self.lu += self.step_time

    def active_update(self):
        spawn = self.spawn
        step_time = self.step_time
        for i in self.characters:
            if random.random() <= 1 - (1 - i[1]) ** (i[2] / 1000):
                i[2] = 0
                spawn(i[0])
            else:
                i[2] += step_time

    def spawn(self, char):
        level = self.level
        size = level.size
        pos = [random.random() * size[0], random.random() * size[1]]
        s = SpawnCircle()
        s.add(level.phys_group)
        s.pos = pos
        e = char(level)
        e.pos = pos


class SurvivalEventSystem(EventSystem):

    def __init__(self, level):
        super().__init__(level)
        SpawnEvent(self)


class Survival(Level):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, size=(8000, 6000), zoom_constraint=[.25, 3.5], **kwargs)

    def pregenerate(self):
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

        from Characters.player_survival import Character as Player

        for _ in range(10):
            s = Soldier(self)
            s.pos = (200, 200)

        self.player = Player(self)
        p_pos = [e / 2 for e in self.size]
        self.player.pos = p_pos
        s = SpawnCircle()
        s.add(self.phys_group)
        s.pos = p_pos

        self.gui = LevelGUI(main=self.main)
        self.event_system = SurvivalEventSystem(self)
        self.score = 0
        self.camera.pos = p_pos
        self.camera.instant_target()

    def add_score(self, val):
        self.score += val

    def end_game(self):
        self.gui.checkout_menu(self.gui.record)

    def draw(self, surface):
        surface.blit(
            pygame.transform.scale(
                self.background.subsurface(self.camera.get_rect().pygame),
                self.screen.size),
            (0, 0))
        super().draw(surface)
        # draw_debug(self.camera, surface, self.phys_group.sprites())
