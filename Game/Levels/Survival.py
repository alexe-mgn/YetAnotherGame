import pygame
import pymunk

from level import Level, EventSystem, Event
from physics import PhysicsGroup
from Game.GUI import LevelGUI
from loading import load_image
from config import *

from VFX.quantum_string import VideoEffect as SpawnCircle
from Characters.Soldier import Character as Soldier
from Characters.Zero import Character as Zero


class SpawnEvent(Event):

    def __init__(self, es):
        super().__init__(es)
        self.characters = [
            ()
        ]


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
        s.pos = p_pos
        self.camera.pos = p_pos
        self.camera.instant_target()
        print(self.camera.rect, self.camera.c_rect)

        self.gui = LevelGUI(main=self.main)
        self.event_system = SurvivalEventSystem(self)
        self.score = 0

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
        # for s in self.phys_group.sprites():
        #     if hasattr(s, 'health') and s.rect.collidepoint(*self.mouse_absolute) and s.own_body():
        #         c = self.camera.world_to_local(s.rect.center)
        #         r = pygame.Rect(0, 0, 50, 10)
        #         r.center = (c[0], c[1] - 20)
        #         pygame.draw.rect(surface, (0, 0, 0), r, 0)
        #         r.inflate_ip(-2, -2)
        #         r.width = r.width * (s.health / s.max_health)
        #         pygame.draw.rect(surface, (0, 255, 0), r, 0)
