import os
from settings import *
import random
from math import pi, sin, cos
from pygame.math import Vector2


def load_image(pygame, file_name, scale_factor=1):

    fullname = os.path.join('graphics', file_name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print("Cannot load image:", file_name)
        raise SystemExit(message)

    image = image.convert_alpha()
    if scale_factor != 1:
        image = pygame.transform.smoothscale(image, (image.get_width() // scale_factor, image.get_height() // scale_factor))

    return image


def load_sound(pygame, file_name):
    """

    :param pygame: pygame object used by the main game
    :param file_name:
    :return:
    """

    # error checking
    class NoneSound:
        def play(self): pass

    if not pygame.mixer:
        return NoneSound()

    fullname = os.path.join('sounds', file_name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print("Cannot load sound:", file_name)
        raise SystemExit(message)
    return sound


def get_random_velocity():
    angle = random.uniform(0, pi * 2)
    x = cos(angle)
    y = sin(angle)

    new_velocity = Vector2(x, y)
    new_velocity.normalize()
    new_velocity *= ANIMAL_SPEED

    return new_velocity


def scale_rect(rect, scale):
    new_size = (scale[0] * rect.width, scale[1] * rect.height)
    rect.size = new_size
    relocate_rect(rect, scale)


def relocate_rect(rect, scale):

    new_pos = (scale[0] * rect.topleft[0], scale[1] * rect.topleft[1])
    rect.topleft = new_pos

def relocate_point(point, scale):
    return (int(scale[0] * point[0]), int(scale[1] * point[1]))
