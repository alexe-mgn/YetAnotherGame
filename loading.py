import pygame
from geometry import Vec2d
from main_settings import get_path
from math import ceil


def load_image(path):
    surface = pygame.image.load(get_path(path)).convert_alpha()
    return surface


def cast_image(source, center, size_inc):
    i_size = Vec2d(source.get_size())
    size = ceil(i_size * size_inc)
    img_center = ceil(center * size_inc)
    h_size = size / 2
    inc_vector = abs(img_center - h_size)
    hf_size = h_size + inc_vector
    tl = ceil(hf_size - img_center)

    img = pygame.Surface(hf_size * 2).convert_alpha()
    img.fill((255, 255, 255, 255))
    img.blit(pygame.transform.scale(source, size),
             tl)
    return img, tl - hf_size