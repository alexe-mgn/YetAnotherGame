import pygame


class Level:

    def __init__(self, size=None):
        self.size = size if size is not None else [1024, 720]
        self.surface = pygame.Surface(self.size)

    def update(self):
        self.render()

    def render(self):
        pass

    def get_image(self, size=None):
        if size is None:
            size = self.size[:]
        return pygame.transform.scale(self.surface, size)
