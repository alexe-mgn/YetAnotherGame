import pygame
from game_class import BaseCreature


class BasePlayer(BaseCreature):

    def __init__(self, level):
        super().__init__()
        self.level = level

    def send_event(self, event):
        pass

    def handle_keys(self):
        if not self.level.paused:
            pressed = pygame.key.get_pressed()
            self.walk((
                int(pressed[pygame.K_d]) - int(pressed[pygame.K_a]),
                int(pressed[pygame.K_s]) - int(pressed[pygame.K_w])
            ))
            if pygame.mouse.get_pressed()[0]:
                self.shot()

    def update(self):
        if not self.level.paused:
            self.angle = (self.level.mouse_absolute - self.pos).angle

    def death(self):
        super().death()
        self.level.end_game()
