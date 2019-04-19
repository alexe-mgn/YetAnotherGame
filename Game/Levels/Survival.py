import pygame
import pymunk

from level import Level, EventSystem, Event
from physics import PhysicsGroup
from Game.GUI import LevelGUI
from loading import load_image
from config import *

from debug_draw import draw_debug
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
        from Characters.Zero import Character as Enemy

        self.player = Player(self)

        # self.player = Player(self)
        # self.player.pos = (500, 500)

        for n in range(5):
            e = Enemy(self)
            e.pos = (1000, 1000)

        self.phys_group = group

        self.gui = LevelGUI(main=self.main)
        self.event_system = SurvivalEventSystem(self)

    def draw(self, surface):
        surface.blit(
            pygame.transform.scale(
                self.background.subsurface(self.camera.get_rect().pygame),
                self.screen.size),
            (0, 0))
        super().draw(surface)
        draw_debug(self.camera, surface, self.phys_group.sprites())
        for s in self.phys_group.sprites():
            if hasattr(s, 'health') and s.rect.collidepoint(*self.mouse_absolute) and s.own_body():
                c = self.camera.world_to_local(s.rect.center)
                r = pygame.Rect(0, 0, 50, 10)
                r.center = (c[0], c[1] - 20)
                pygame.draw.rect(surface, (0, 0, 0), r, 0)
                r.inflate_ip(-2, -2)
                r.width = r.width * (s.health / s.max_health)
                pygame.draw.rect(surface, (0, 255, 0), r, 0)
        # pygame.draw.circle(surface, (0, 255, 0), [int(e) for e in self.camera.world_to_local(self.player.get_mount(key='engine').object.pos)], 3)
        # pygame.draw.circle(surface, (255, 0, 0), [int(e) for e in self.camera.world_to_local(self.player.pos)], 3)
