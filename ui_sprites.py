import pygame
import settings
from game_sprites import FiniteStateMachine


class Paw(pygame.sprite.DirtySprite):
    def __init__(self, image, image_deactivate, position):
        pygame.sprite.DirtySprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position
        self._position = position
        self.image_deactivate = image_deactivate
        self.active = True

    def deactivate(self):
        # Lisää pieni animaatio

        self.image = self.image_deactivate
        self.dirty = 1
        self.active = False

    def is_active(self):
        return self.active

    def update(self, dt):
        pass

    def scale(self, image_active, image_deactive):
        if self.active:
            self.image = image_active
        else:
            self.image = image_deactive

        self.image_deactivate = image_deactive

        self.rect.size = self.image.get_rect().size
        new_x = int(self.rect.topleft[0] * settings.scale_factor[0])
        new_y = int(self.rect.topleft[1] * settings.scale_factor[1])
        self.rect.topleft = (new_x, new_y)


class Fence(pygame.sprite.DirtySprite):
    def __init__(self, image, position):
        pygame.sprite.DirtySprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.position = position

    def update(self, dt):
        # Nothing to update
        pass

    def scale(self, image):
        self.image = image
        new_x = int(self.rect.topleft[0] * settings.scale_factor[0])
        new_y = int(self.rect.topleft[1] * settings.scale_factor[1])
        self.rect.topleft = (new_x, new_y)
        self.rect.size = self.image.get_rect().size


class Exclamation(pygame.sprite.DirtySprite):
    def __init__(self, image):
        pygame.sprite.DirtySprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.visible = 0
        self._call_start_time = 0

    def show_exclamation(self, other_position):
        self.rect.bottomright = other_position
        self.visible = 1
        self.dirty = 1

    def hide_exclamation(self):
        self.visible = 0
        self.dirty = 1

    def update(self, dt):
        pass

    def move(self, animal_position):
        self.dirty = 1
        self.rect.bottomright = animal_position


class Gate(pygame.sprite.DirtySprite):
    def __init__(self, image, position, owner):
        pygame.sprite.DirtySprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self._speed = settings.GATE_SPEED
        self.owner = owner
        self._brain = FiniteStateMachine(self._closed, "closed")

    def close_gate(self):
        self._brain.set_state(self._move_up, "move_up")


    def open_gate(self):
        self._brain.set_state(self._move_down, "move_down")

    def _closed(self, dt):
        pass

    def _open(self, dt):
        pass

    def _move_up(self, dt):
        if self.rect.top > settings.SCREEN_HEIGHT * 0.35:
            self.rect.y -= self._speed
            self.dirty = 1
        else:
            self._brain.set_state(self._closed, "closed")

    def _move_down(self, dt):

        if self.rect.centery < settings.SCREEN_HEIGHT * 0.82:
            self.rect.y -= -self._speed
            self.dirty = 1
        else:
            self._brain.set_state(self._open, "open")

    def get_state(self):
        return self._brain.get_state()

    def update(self, dt):
        self._brain.update(dt)
        #if self.owner.get_state() == "wait_for_animal":
        #if self.owner.get_state() == "walk_away":

    def scale(self, image):
        self.image = image
        new_x = int(self.rect.topleft[0] * settings.scale_factor[0])
        new_y = int(self.rect.topleft[1] * settings.scale_factor[1])
        self.rect.topleft = (new_x, new_y)
        self.rect.size = self.image.get_rect().size


class Heard(pygame.sprite.DirtySprite):
    def __init__(self, image):
        pygame.sprite.DirtySprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()
        self.visible = 0
        self._heard_start_time = 0

    def show_heard(self, other_position):
        self.rect.midbottom = other_position
        self.visible = 1
        self.dirty = 1

    def hide_heard(self):
        self.visible = 0
        self.dirty = 1

    def update(self, dt):
        pass

    def move(self, animal_position):
        self.dirty = 1
        self.rect.midbottom = animal_position
