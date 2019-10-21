import pygame
import pymunk

from Engine.level import Level, Event
from Engine.physics import PhysicsGroup
from Game.GUI import LevelGUI
from Engine.loading import load_image

from VFX.quantum_string import VideoEffect as SpawnCircle
from Characters.Soldier import Character as Soldier
from Characters.Zero import Character as Zero
from Objects.Medkit import Object as Medkit
from Engine.level import EventSystem

import random


class SpawnEvent(Event):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lu = 0
        self.objects = [
            [Soldier, .5, 0],
            [Zero, .1, 0],
            [Medkit, .005, 0]
        ]

    def update(self):
        if not self.level.paused:
            self.lu += self.step_time

    def active_update(self):
        spawn = self.spawn
        step_time = self.step_time
        for i in self.objects:
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
        s.position = pos
        e = char(level)
        e.position = pos


class SurvivalEventSystem(EventSystem):

    def __init__(self, level):
        super().__init__(level)
        self.add(SpawnEvent())


class SurvivalPhysGroup(PhysicsGroup):

    def add_internal(self, sprite):
        super().add_internal(sprite)
        if sprite.damping is None:
            sprite.damping = 1


class Survival(Level):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, size=(8000, 6000), zoom_constraint=[.25, 3.5], **kwargs)

    def pregenerate(self):
        self.background = pygame.transform.scale(load_image('Game\\Levels\\background.jpg', alpha=False), self.size)

        space = pymunk.Space()
        space.damping = 1
        space.gravity = [0, 0]
        group = SurvivalPhysGroup(space)
        self.phys_group = group

        level_rect = self.get_world_rect()
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
            s.position = (200, 200)

        self.gui = LevelGUI(main=self.main)
        self.event_system = SurvivalEventSystem(self)
        self.score = 0

        p_pos = [e / 2 for e in self.size]
        self.camera.position = p_pos
        self.camera.instant_move()

        self.player = Player(self, gui=self.gui.ingame)
        self.player.position = p_pos
        s = SpawnCircle()
        s.add(self.phys_group)
        s.position = p_pos

        self.gui.ingame.player = self.player

    def add_score(self, val):
        self.score += val

    def end_game(self):
        self.gui.checkout_menu(self.gui.record)

    def draw(self, surface):
        from Engine.geometry import Vec2d
        surface.blit(
            pygame.transform.scale(
                self.background.subsurface(self.camera.get_rect().pygame),
                self.screen.size),
            self.screen.topleft)
        # print(self.player.angle, (self.mouse_world - self.player.pos).angle)
        super().draw(surface)
        # draw_debug(self.camera, surface, self.phys_group.sprites())
