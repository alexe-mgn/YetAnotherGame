import pygame
from main_settings import get_path


def load_image(path):
    surface = pygame.image.load(get_path(path)).convert_alpha()
    return surface
