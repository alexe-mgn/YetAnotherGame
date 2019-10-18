from Projectiles.pulson import Projectile

from Engine.config import TEAM
from Engine.level import Level
from Engine.physics import PhysicsGroup

import pygame
import pymunk

drag_sprite = None


class TestLevel(Level):

    def pregenerate(self):
        space = pymunk.Space()
        space.damping = 1
        space.gravity = [0, 0]

        group = PhysicsGroup(space)
        from Weapons.pulson import Weapon
        w = Weapon()
        w.add(group)
        w.pos = (300, 300)
        self.w = w
        w = Weapon()
        w.add(group)
        w.pos = (300, 300)
        from Objects.MechZero import Creature
        from Components.LegsZero import Engine
        mc = Creature()
        mc.add(group)
        mc.pos = (500, 500)
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

    def get_mouse_sprite(self):
        for s in self.phys_group.layer_sorted()[::-1]:
            if s.shape.point_query(self.mouse_absolute)[0] <= 0:
                return s
        return None

    def send_event(self, event):
        super().send_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            global drag_sprite
            s = self.get_mouse_sprite()
            if event.button == 1:
                if drag_sprite is not None:
                    drag_sprite.vel = (self.mouse_absolute - self.mouse_absolute_prev) / self.step_time * 1000
                    drag_sprite = None
                elif s is not None:
                    if drag_sprite is None:
                        drag_sprite = s
            elif event.button == 2:
                if hasattr(s, 'fire'):
                    s.fire()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                proj = Projectile()
                proj.add(self.phys_group)
                proj.fire(self.mouse_absolute.angle, 1000)
            elif event.key == pygame.K_g:
                self.w.fire()
            elif event.key == pygame.K_l:
                self.camera.center = self.player.pos

    def end_step(self):
        super().end_step()
        global drag_sprite
        # print(drag_sprite, self.mouse_absolute)
        if drag_sprite is not None:
            if drag_sprite.space:
                drag_sprite.pos = self.mouse_absolute
                drag_sprite.vel = [0, 0]
            else:
                drag_sprite = None

    def handle_keys(self):
        super().handle_keys()

    def draw(self, surface):
        super().draw(surface)
        tl = self.camera.world_to_local((0, 0))
        br = self.camera.world_to_local(self.screen)
        pygame.draw.line(surface, (255, 0, 0), tl, br)
        pygame.draw.rect(surface, (0, 255, 0), self.screen, 1)
