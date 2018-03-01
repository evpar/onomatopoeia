import pygame
import settings
from help_functions import relocate_rect, scale_rect


class FiniteStateMachine():
    def __init__(self, state=None, state_str=""):
        self.__active_state = state
        self.__state_str = state_str

    def set_state(self, new_state_function, new_state_str=""):
        self.__active_state = new_state_function
        self.__state_str = new_state_str

    def get_state(self):
        return self.__state_str

    def update(self, dt):
        if self.__active_state is not None:
            self.__active_state(dt)


class Animal(pygame.sprite.DirtySprite):
    def __init__(self, velocity, species, exclamation, heard_call, shadow, position, animation_images):
        """
        An animal. They move in a straight and bounce from the borders. Can be called by the player.
        :param velocity: The velocity of the animal (direction and speed)
        :param species: The species of the animal
        :param position: The topleft position as tuple (x, y)
        :param image: The image for the animal
        """
        pygame.sprite.DirtySprite.__init__(self)  # Call Sprite initializer

        self.image = animation_images[0]
        self.rect = self.image.get_rect()
        self.collision_rect = self.rect.inflate(-1, -1)
        self.rect.topleft = position
        self.velocity = velocity
        self.species = species
        self.exclamation = exclamation
        self.heard_call = heard_call
        self.shadow = shadow
        self.position = position
        self.speed = settings.ANIMAL_SPEED
        self.dirty = 2
        self.hit_gate = False
        # for checking collision with call radius circle
        self.mask = pygame.mask.from_surface(self.image)
        self._shout_start_time = 0
        self._heard_start_time = 0
        self._animation_images = animation_images

        # variables for animation
        self.counter = 0
        self.animation_index = 0

        self.owner_position = None
        self._brain = FiniteStateMachine(self.move_in_play_area, "move_in_play_area")

    def update(self, dt):

        self._brain.update(dt)
        #self.move_in_play_area(dt)
        # Borders around animals, for debugging
        #pygame.draw.rect(self.image, (0, 0, 255), self.collision_rect, 1)
        if self.exclamation.visible and pygame.time.get_ticks() - self._shout_start_time > settings.EXCLAMATION_MARK_VISIBLE_TIME_MS:
            self._shout_start_time = 0
            self.exclamation.hide_exclamation()
        
        if self.heard_call.visible and pygame.time.get_ticks() - self._heard_start_time > settings.HEARD_CALL_VISIBLE_TIME_MS:
            self._heard_start_time = 0
            self.heard_call.hide_heard()

    def move_with_owner(self, dt):

        self.move_animation(dt)
        self.rect.x = self.owner_position.centerx
        self.rect.bottom = self.owner_position.bottom

    def move_to_owner(self, dt):
        self.move_animation(dt)

        if self.position[0] < self.owner_position.centerx:
            self._move(dt)
        else:
            self._brain.set_state(self.move_with_owner, "move_with_owner")

    def go_to_owner(self, owner_position):
        self.owner_position = owner_position
        self.turn_towards_point(pygame.math.Vector2(owner_position.center))
        self._brain.set_state(self.move_to_owner, "move_to_owner")

    def move_animation(self, dt):

        # Animation for the movement
        self.counter += dt
        if self.counter > 90:
            self.image = self._animation_images[self.animation_index]
            self.animation_index = (self.animation_index + 1) % len(self._animation_images)
            self.counter = 0

        self.shadow.move(self.rect.midbottom)

    def _move(self, dt):

        self.move_animation(dt)

        # Actual movement
        self.position += (self.velocity[0] * settings.scale_factor[0] * (dt / 100),
                          self.velocity[1] * settings.scale_factor[1] * (dt / 100))
        self.rect.x = round(self.position.x)
        self.rect.y = round(self.position.y)

    def move_in_play_area(self, dt):

        self.hit_gate = False
        old_position = self.position

        # Actual movement
        self._move(dt)

        # Collision detection with gate
        if settings.gate.collidepoint(self.rect.topright) and settings.gate.collidepoint(self.rect.bottomright):
            self.hit_gate = True
            self.position = old_position
            self.velocity.x *= -1
            self._animation_images = [pygame.transform.flip(img, True, False) for img in self._animation_images]

        # Collision detection with borders
        if self.rect.x < settings.play_area.left or self.rect.x > settings.play_area.right - self.rect.width:
            self.velocity.x *= -1
            self._animation_images = [pygame.transform.flip(img, True, False) for img in self._animation_images]
            self.position = old_position

        if self.rect.y < settings.play_area.top or self.rect.y > settings.play_area.bottom - self.rect.height:
            self.velocity.y *= -1
            self.position = old_position

        if self.heard_call.visible == 1:
            self.heard_call.move(self.rect.midtop)

        if self.exclamation.visible == 1:
            self.exclamation.move(self.rect.topright)

    def turn_towards_point(self, point):
        """
        Turn the movement of animal towards the player
        :param player_position: The position to turn the animal towards (pygame.math.Vector2)
        :return: -
        """
        new_dir = point - self.rect.center
        new_velocity = new_dir.normalize()

        # Flip the animation images if the animal changes direction on x axis
        if new_velocity[0] * self.velocity[0] < 0:
            self._animation_images = [pygame.transform.flip(img, True, False) for img in self._animation_images]

        self.velocity = new_velocity * self.speed

    def get_state(self):
        return self._brain.get_state()

    def scale(self, images):
        self.image = images[self.animation_index]
        self._animation_images = images

        # Calculate new position
        relocate_rect(self.rect, settings.scale_factor)
        self.rect.size = self.image.get_rect().size

        self.collision_rect = self.rect.inflate(-1, -1)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.DirtySprite):
    def __init__(self, animation_images, position, speed, circle, speech_bubble, shadow):
        """
        The player sprite.
        :param image: image for the player
        :param position: The start position of the player (center point)
        :param speed: The speed of the player
        :param circle: The call circle sprite used to indicate the call radius around the player
        :param speech_bubble: The speech bubble sprite used to indicate the player is making a call
        """
        pygame.sprite.DirtySprite.__init__(self)

        # Variables image and rect are required by the Sprite super class
        self._animation_images = animation_images
        self._animation_index = 0
        self.image = animation_images[0]
        self.rect = self._animation_images[0].get_rect()
        self.rect.center = position

        self.speed = speed
        self._position = position
        self._circle = circle
        self._speech_bubble = speech_bubble
        self._shadow = shadow
        self._calling_animal = False    # Is player currently calling an animal
        self._call_start_time = 0       # Start time of a call
        self.counter = 0


    def scale(self, images, bubble_image, animal_images):
        self._animation_images = images

        self.rect.size = self.image.get_rect().size
        relocate_rect(self.rect, settings.scale_factor)

        self._speech_bubble.scale(bubble_image, animal_images)
        self._circle.scale_circle(self.rect)

    def redraw_circle(self):
        self._circle.dirty = 1

    def update(self, dt):

        # If player is not calling an animal, move.
        # Otherwise, if the player is calling an animal, check if calling can be stopped.
        #if self._calling_animal == False:
        self.move(dt)

        if self._speech_bubble.visible and pygame.time.get_ticks() - self._call_start_time > settings.SPEECH_BUBBLE_VISIBLE_TIME_MS:
                self._call_start_time = 0
                self._speech_bubble.hide_bubble()
                self._calling_animal = False

    def move_animation(self, dt):

        # Animation for the movement
        self.counter += dt
        if self.counter > 0.90:
            self.image = self._animation_images[self._animation_index]
            self._animation_index = (self._animation_index + 1) % len(self._animation_images)
            self.counter = 0

    def move(self, dt):


        # Convert dt to seconds
        dt /= 100

        # Get the current state of keys
        keys = pygame.key.get_pressed()

        # Move the player
        if keys[pygame.K_LEFT]:
            self.rect.x -= int(self.speed * settings.scale_factor[0] * dt)
            self.dirty = 1
            self.move_animation(dt)
        if keys[pygame.K_RIGHT]:
            self.rect.x += int(self.speed * settings.scale_factor[0] * dt)
            self.dirty = 1
            self.move_animation(dt)
        if keys[pygame.K_UP]:
            self.rect.y -= int(self.speed * settings.scale_factor[1] * dt)
            self.dirty = 1
            self.move_animation(dt)
        if keys[pygame.K_DOWN]:
            self.rect.y += int(self.speed * settings.scale_factor[1] * dt)
            self.dirty = 1
            self.move_animation(dt)
            #self.counter = (self.counter + 1) % len(self._animation_images)


        # prevent the player from going outside the play area
        self.rect.clamp_ip(settings.play_area)
        self._position = pygame.math.Vector2(self.rect.center)
        
        self._shadow.move(self.rect.midbottom)

        # Move the call radius circle if the player was moved
        if self.dirty == 1:
            self._circle.move(self._position)
            self._speech_bubble.move(self.rect)

    def call_animal(self, animal_type, animal_list):
        """
        Make a call. Turn nearby animals of a type towards the player.
        :param animal_type: The type of animal called
        :param animal_lists: List of containing lists of animals
        :return: -
        """

        # A new call cannot be made before the old call is finished.
        if self._calling_animal:
            return

        # Show speech bubble
        self._speech_bubble.show_bubble(self.rect, animal_type)
        self._calling_animal  = True
        self._call_start_time = pygame.time.get_ticks()

        collided = pygame.sprite.spritecollide(self._circle, animal_list, False, pygame.sprite.collide_mask)

        for animal in collided:
            animal.turn_towards_point(self._position)
            animal.heard_call.show_heard(animal.rect.midtop)
            animal._heard_start_time = pygame.time.get_ticks()

    def is_calling(self):
        """
        Returns a boolean indicating whether the player is currently calling an animal.
        :return: boolean
        """
        return self._calling_animal


class Owner(pygame.sprite.DirtySprite):

    def __init__(self, image, image_id, speech_bubble, exclamation, position, animal_type, shadow):
        """
        Owner sprite. It is the customer in the game who walks from the bottom of the screen to the gate and ask for
        an animal. Once he gets what he wants he walks away.

        :param image: image for the sprite
        :param speech_bubble: Bubble sprite used to indicate the animal the owner wants
        :param position: The top left position of the sprite
        :param animal_type: The type of animal the owner wants
        """
        pygame.sprite.DirtySprite.__init__(self)

        self.image = image
        self.image_id = image_id
        self.rect = image.get_rect()
        self.rect.center = position
        self._speech_bubble = speech_bubble
        self._exclamation = exclamation
        self._shadow = shadow
        self._speed = 2
        self.animal = animal_type

        self._start_time = 0
        self._shout_start_time = 0
        self._speed_scale = (1, 1)
        self._brain = FiniteStateMachine(self.walk_to_gate, "walk_to_gate")

        self.animal_sprite = None

    def walk_to_gate(self, dt):
        # Walk to the gate
        if self.rect.centery > settings.play_area.centery:
            self.move()
        else:
            # The owner reached the gate, ask for an animal
            self._speech_bubble.show_bubble(self.rect, self.animal)
            self._brain.set_state(self.wait_for_animal, "wait_for_animal")

    def wait_for_animal(self, dt):
        pass

    def walk_away(self, dt):
        self.move()
        # Customer walked out of the screen -> destroy it
        if self.rect.y < - self.rect.height:
            self.kill()
            self.animal_sprite.kill()
            self.animal_sprite.shadow.kill()

    def get_animal(self):
        """
        The owner gets the animal it wanted. This causes it to walk away.
        :return: -
        """

        self._speech_bubble.hide_bubble()
        self._brain.set_state(self.walk_away, "walk_away")

    def get_state(self):
        return self._brain.get_state()

    def move(self):
        self.rect.y -= (self._speed * settings.scale_factor[1])
        self.dirty = 1
        self._shadow.move(self.rect.midbottom)

    def scale(self, image, bubble_image, animal_images):
        self.image = image
        scale_rect(self.rect, settings.scale_factor)

        self._speech_bubble.scale(bubble_image, animal_images)
        if self._speech_bubble.visible:
            self._speech_bubble.show_bubble(self.rect, self.animal)

    def update(self, dt):

        self._brain.update(dt)
        if self._exclamation.visible and pygame.time.get_ticks() - self._shout_start_time > settings.EXCLAMATION_MARK_VISIBLE_TIME_MS:
            self._shout_start_time = 0
            self._exclamation.hide_exclamation()


class Circle(pygame.sprite.DirtySprite):
    def __init__(self, player_size):
        pygame.sprite.DirtySprite.__init__(self)

        self.image = None
        self.rect = None
        self.mask = None

        self.scale_circle(player_size)

    def move(self, position):
        """
        Move the circle to a new position
        :param position: Point where the center of the circle is moved to. Tuple of type (x, y)
        :return: -
        """
        self.rect.center = position
        self.dirty = 1

    def update(self, dt):
        pass

    def scale_circle(self, player_rect):


        call_circle_radius = int(1.5 * player_rect.width)

        # Create a transparent surface for the circle
        self.image = pygame.Surface((2 * call_circle_radius, 2 * call_circle_radius), pygame.SRCALPHA, 32)
        # Draw a transparent circle on the surface
        pygame.draw.circle(self.image, settings.CALL_CIRCLE_COLOR, (call_circle_radius, call_circle_radius), call_circle_radius)
        self.rect = self.image.get_rect()
        # Create mask for collision detection with the animals

        self.mask = pygame.mask.from_surface(self.image, settings.CALL_CIRCLE_COLOR[3] - 3)


        # Move to new place
        self.move(player_rect.center)


class Bubble(pygame.sprite.DirtySprite):
    """
    A sprite class for the speech bubble indicating that player is calling an animal.
    """
    def __init__(self, bubble_image, animal_images):
        pygame.sprite.DirtySprite.__init__(self)

        self.bubble_image = bubble_image.copy()
        self.image = bubble_image
        self.rect = self.image.get_rect()

        # Hide the bubble
        self.visible = 0

        # Scale all animals to right size for the bubble
        self._animal_images = {}
        for animal in animal_images:
            new_width = int(0.5*animal_images[animal][0].get_rect().width)
            new_height = int(0.5*animal_images[animal][0].get_rect().height)
            self._animal_images[animal] = pygame.transform.smoothscale(animal_images[animal][0], (new_width, new_height))

    def show_bubble(self, player_position, animal):
        """
        Show speech bubble indicating the animal player is calling
        :param player_position: player sprite's rect
        :param animal: Called animal
        :return: -
        """

        self.image = self.bubble_image.copy()
        img_rect = self._animal_images[animal].get_rect()
        img_rect.center = self.image.get_rect().center
        self.image.blit(self._animal_images[animal], img_rect.topleft)

        self.rect.bottomleft = (player_position.right - self.rect.width // 2, player_position.top)
        self.visible = 1
        self.dirty = 1

    def hide_bubble(self):
        """
        Hide speech bubble
        :return: -
        """
        self.visible = 0
        self.dirty = 1

    def update(self, dt):
        pass

    def move(self, player_position):
        self.dirty = 1
        self.rect.bottomleft = player_position.right - self.rect.width // 2, player_position.top


    def scale(self, image, animal_images):
        self.bubble_image = image.copy()
        relocate_rect(self.rect, settings.scale_factor)
        for animal in animal_images:
            new_width = int(0.5 * animal_images[animal][0].get_rect().width)
            new_height = int(0.5 * animal_images[animal][0].get_rect().height)
            self._animal_images[animal] = pygame.transform.smoothscale(animal_images[animal][0], (new_width, new_height))

class Shadow(pygame.sprite.DirtySprite):
    def __init__(self, image):
        pygame.sprite.DirtySprite.__init__(self)

        self.image = image
        self.rect = self.image.get_rect()

    def update(self, dt):
        pass

    def move(self, position):
        self.dirty = 1
        self.rect.midbottom = (position[0],position[1]+3)