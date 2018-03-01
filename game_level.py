import pygame
from pygame.locals import *
from help_functions import *
from game_sprites import Animal, Player, Circle, Bubble, Owner, Shadow
from ui_sprites import Paw, Fence, Exclamation, Gate, Heard
from game_state import GameState
import settings


class GameLevel(GameState):
    def __init__(self, animals, background, player_images, animal_images, bubble_images, owner_images, paw_images,
                 fence_images, exclamation_image, gate_image, heard_image, shadow_image, sound_event_interface):
        """
        A single level on the game.

        :param animals:
        :param background: The background image for the game level
        :param player_image: list of images for player animation
        :param animal_images: dict containing a list of animal images for each animal
        :param bubble_images: list of different speech bubble images
        :param owner_images: list of different owner images
        :param paw_images: list containing images for active and deactive paw
        :param fence_images: list or fence images
        :param exclamation_image: image of an exclamation mark for wrong animal hitting the gate
        :param gate_image: image for the game
        :param heard_image: a question mark image for indicating that the animal has heard a call
        :param shadow_image: a shadow image underneath the characters
        :param sound_event_interface: an object of SoundEventInterface which takes care of the audio input and classification.
        """

        super(GameLevel, self).__init__()

        # Images used in the level
        self._animal_images = animal_images
        self._bubble_images = bubble_images
        self.background = background
        self._player_images = player_images
        self._UI_paw_active = paw_images[0]
        self._UI_paw_deactive = paw_images[1]
        self._fence_front_image = fence_images[0]
        self._fence_back_image = fence_images[1]
        self._fence_left_image = fence_images[2]
        self._fence_right_image = fence_images[3]
        self._owner_images = owner_images
        self._exclamation_image = exclamation_image
        self._heard_image = heard_image
        self._gate_image = gate_image
        self._shadow_image = shadow_image

        # Containers for the sprites
        self._all_sprites = None
        self._animal_sprites = None
        self._paw_sprites = None

        self._animals_on_level = animals

        # Sprites
        self._life_symbols = []
        self._animal_sprites_grouped_dict = {}
        self._player = None
        self._call_circle = None
        self._owner_sprite = None
        self._gate_sprite = None
        self._fences = {}

        self.pause = False
        self.remaining_lives = 0
        self.sound_effect_interface = sound_event_interface

    def give_scaled_graphics(self, background, player_images, animal_images, bubble_images, owner_images, paw_images,
                             fence_images, gate_image):
        """
        Give the level new images which are resized to the new window size. Also repositions the elements on the screen.
        :param background: Background image of the game level
        :param player_image: Image for the player
        :param animal_images: dict containing a list of animal images for each animal
        :param bubble_images: list of images for speech bubbles
        :param owner_images: list of owner images
        :param paw_images: list of paw images [active paw, deactive paw]
        :param fence_images: list of fence images
        :param gate_image: game image
        :return: -
        """

        # Images used in the level
        self._animal_images = animal_images
        self._bubble_images = bubble_images
        self.background = background
        self._player_images = player_images
        self._UI_paw_active = paw_images[0]
        self._UI_paw_deactive = paw_images[1]
        self._fence_front_image = fence_images[0]
        self._fence_back_image = fence_images[1]
        self._fence_left_image = fence_images[2]
        self._fence_right_image = fence_images[3]
        self._gate_image = gate_image
        self._owner_images = owner_images

        # If level has not been started, these do not exist and there is no reason to relocate
        try:

            for animal in self._animal_sprites_grouped_dict:
                for sprite in self._animal_sprites_grouped_dict[animal]:
                    sprite.scale(self._animal_images[animal])

            self._player.scale(self._player_images, self._bubble_images[0], self._animal_images)
            self._owner_sprite.scale(self._owner_images[self._owner_sprite.image_id], self._bubble_images[0],
                                     self._animal_images)

            for animal in self._animal_sprites_grouped_dict:
                for sprite in self._animal_sprites_grouped_dict[animal]:
                    sprite.scale(self._animal_images[animal])

            for paw in self._paw_sprites:
                paw.scale(self._UI_paw_active, self._UI_paw_deactive)

            self._fences["left"].scale(self._fence_left_image)
            self._fences["right"].scale(self._fence_right_image)
            self._fences["back"].scale(self._fence_back_image)
            self._fences["front"].scale(self._fence_front_image)

            self._gate_sprite.scale(self._gate_image)
        except AttributeError:
            pass

    def start_new(self):
        """
        Start level from the beginning. This method initializes and creates everything.
        :return: -
        """

        # Reset background
        self.screen.blit(self.background, (0, 0))
        pygame.display.update()

        self.remaining_lives = NUMBER_OF_LIVES - 1

        # Group containers for sprites
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.RenderUpdates
        self._animal_sprites = pygame.sprite.LayeredDirty()
        self._all_sprites = pygame.sprite.LayeredDirty()
        self._paw_sprites = pygame.sprite.LayeredDirty()
        self._animal_sprites_grouped_dict = {animal: pygame.sprite.LayeredDirty() for animal in self._animal_images.keys()}

        # Play area fences
        fence_back = Fence(self._fence_back_image, settings.FENCE_BACK)
        self._all_sprites.add(fence_back)
        fence_left = Fence(self._fence_left_image, settings.FENCE_LEFT)
        self._all_sprites.add(fence_left)
        fence_right = Fence(self._fence_right_image, settings.FENCE_RIGHT)
        self._all_sprites.add(fence_right)

        # Create animals
        for species in self._animals_on_level:
            size = self._animal_images[species][0].get_size()  # return tuple (width,height)

            x = random.randint(size[0], play_area.right - size[0])
            y = random.randint(size[1], play_area.bottom - size[1])
            velocity = get_random_velocity()

            # Local copies so that if there would ever be several animals of the same species
            # the flips would go correctly
            images = self._animal_images[species].copy()
            if velocity[0] > 0:
                images = [pygame.transform.flip(img, True, False) for img in images]

            animal_exclamation = Exclamation(self._exclamation_image)
            heard = Heard(self._heard_image)
            shadow = Shadow(self._shadow_image)
            new_animal = Animal(velocity, species, animal_exclamation, heard, shadow, Vector2(x, y),images)

            self._animal_sprites.add(new_animal)
            self._all_sprites.add(shadow)
            self._all_sprites.add(new_animal)
            self._all_sprites.add(animal_exclamation)
            self._all_sprites.add(heard)
            self._animal_sprites_grouped_dict[species].add(new_animal)

        # Player starting position (in the middle of the play area)
        starting_position = Vector2(play_area.centerx, play_area.centery)

        # Create circle indicating call radius
        self._call_circle = Circle(self._player_images[0].get_rect())
        self._all_sprites.add(self._call_circle)

        # Create speech bubble for player
        player_speech_bubble = Bubble(self._bubble_images[0], self._animal_images)
        self._all_sprites.add(player_speech_bubble)
        
        player_shadow = Shadow(self._shadow_image)
        self._all_sprites.add(player_shadow)

        # Create player
        self._player = Player(self._player_images, starting_position, PLAYER_SPEED, self._call_circle, player_speech_bubble, player_shadow)
        self._all_sprites.add(self._player)

        # Create owner
        self._create_owner()

        # paw_position = PAW_POS
        paw_position = list(settings.PAW_POS)

        # Create UI paws
        for i in range(NUMBER_OF_LIVES):
            UI_paws = Paw(self._UI_paw_active, self._UI_paw_deactive, paw_position)
            self._all_sprites.add(UI_paws)
            self._paw_sprites.add(UI_paws)
            self._life_symbols.append(UI_paws)
            paw_position[0] = paw_position[0] + int(1.05 * self._UI_paw_active.get_width())

        # Front fence
        fence_front = Fence(self._fence_front_image, settings.FENCE_FRONT)
        self._all_sprites.add(fence_front)
        self._fences = {"left": fence_left, "right": fence_right, "back": fence_back, "front": fence_front}

        # Gate for the play area
        self._gate_sprite = Gate(self._gate_image, (settings.SCREEN_WIDTH * 0.81, settings.SCREEN_HEIGHT * 0.35),
                                 self._owner_sprite)
        self._all_sprites.add(self._gate_sprite)

        # Start audio threads
        self.sound_effect_interface.start_threads()

    def _create_owner(self):
        """
        Creates an owner sprite.
        :return: -
        """
        owner_speech_bubble = Bubble(random.choice(self._bubble_images), self._animal_images)
        owner_exclamation = Exclamation(self._exclamation_image)
        wanted_animal = random.randint(0, len(self._animal_sprites) - 1)
        image_index = random.randint(0, len(self._owner_images) - 1)
        owner_shadow = Shadow(self._shadow_image)

        pos_x = (self.screen.get_width() - play_area.right) // 2 + play_area.right
        self._owner_sprite = Owner(self._owner_images[image_index], image_index, owner_speech_bubble, owner_exclamation,
                                   (pos_x, self.screen.get_height() + self._owner_images[0].get_height()),
                                   self._animal_sprites.get_sprite(wanted_animal).species, owner_shadow)
        self._all_sprites.add(owner_shadow)
        self._all_sprites.add(self._owner_sprite)
        self._all_sprites.add(owner_speech_bubble)
        self._all_sprites.add(owner_exclamation)

    def _check_gate_collision(self):
        """
        Checks and handles animal collisions with the gate. If a wanted animal collides with the gate it gets destroyed
        and the owner leaves. If an unwanted animal hits the gate, the player loses one life. If all lives are lost,
        the game ends.
        :return: -
        """

        # Check collision with the gate
        for animal_sprite in self._animal_sprites:

            # The animal has walked to the owner
            if animal_sprite.get_state() == "move_with_owner" and self._owner_sprite.get_state() == "wait_for_animal":
                self._gate_sprite.close_gate()
                self._owner_sprite.get_animal()

            if animal_sprite.hit_gate and animal_sprite.get_state() == "move_in_play_area" and \
                    self._owner_sprite.get_state() == "wait_for_animal":

                # Wanted animal hit gate
                if animal_sprite.species == self._owner_sprite.animal:
                    self._owner_sprite.animal_sprite = animal_sprite
                    animal_sprite.go_to_owner(self._owner_sprite.rect)

                    animal_sprite.exclamation.kill()
                    animal_sprite.heard_call.kill()

                    # fixes bug with transparency when animal is removed when it's touching the call circle
                    self._player.redraw_circle()

                else:
                    # Unwanted animal hit gate -> take a life point
                    animal_sprite.exclamation.show_exclamation(animal_sprite.rect.topright)
                    animal_sprite._shout_start_time = pygame.time.get_ticks()
                    
                    self._owner_sprite._exclamation.show_exclamation(self._owner_sprite.rect.topleft)
                    self._owner_sprite._shout_start_time = pygame.time.get_ticks()
                    
                    used = 0
                    for paw in reversed(self._life_symbols):
                        used += 1
                        if paw.is_active():
                            paw.deactivate()
                            break

                    if used == NUMBER_OF_LIVES:
                        self.draw()  # deactivates the last paw on the screen
                        self.sound_effect_interface.stop_audio()
                        GameState.game_state_manager.get_state("game_ended_menu").set_text("Game over!")
                        GameState.game_state_manager.set_state("game_ended_menu")

    def update(self, dt):

        # Check whether the level has been won
        # (no animals in the gate and the owner has walked away)
        if len(self._animal_sprites) == 0 and not self._owner_sprite.alive():
            self.sound_effect_interface.stop_audio()

            # The whole game has been won
            if GameState.game_state_manager.get_current_state_name() == "level_4":
                GameState.game_state_manager.get_state("game_ended_menu").set_text("Game won!")
                GameState.game_state_manager.set_state("game_ended_menu")
            else:
                # single level has been won
                name = GameState.game_state_manager.get_current_state_name()
                GameState.game_state_manager.set_state("next_level_menu")
                GameState.game_state_manager.get_current_state().previous_state_name = name

            return

        # If an owner does not exist -> create one
        if not self._owner_sprite.alive():
            self._create_owner()

        if self._gate_sprite.get_state() == "closed" and self._owner_sprite.get_state() == "wait_for_animal":
            self._gate_sprite.open_gate()

        # Check and handle animals hitting the gate if the gate is open
        if self._gate_sprite.get_state() == "open":
            self._check_gate_collision()

        # Check and handle an animal call
        # Update player status to sound event interface
        if self.sound_effect_interface.calling != self._player.is_calling():
            self.sound_effect_interface.calling = self._player.is_calling()

        # if the player is not calling, check for a call
        if self._player.is_calling() == False:
            call = self.sound_effect_interface.get_animal_call()
            if call != None:
                self._player.call_animal(call, self._animal_sprites_grouped_dict[call])

        # call update function for all sprites
        self._all_sprites.update(dt)

    def get_event(self, event):
        """
        Handle user events
        :param event: an event a user has created (key press, mouse click etc)
        :return: -
        """

        # Quit the game when player closes the game window from x
        if event.type == QUIT:
            self.sound_effect_interface.stop_audio()
            self.quit = True

        elif event.type == KEYDOWN:
            # Pause the game and open menu
            if event.key == K_SPACE or event.key == K_RETURN or event.key == K_ESCAPE:
                self.sound_effect_interface.stop_audio()
                state_name = GameState.game_state_manager.get_current_state_name()
                GameState.game_state_manager.push_state("pause_menu")
                GameState.game_state_manager.get_current_state().previous_state_name = state_name

            # Cheat buttons for animal calls
            elif event.key == K_a:
                self._player.call_animal("cat", self._animal_sprites_grouped_dict["cat"])
            elif event.key == K_s:
                self._player.call_animal("cow", self._animal_sprites_grouped_dict["cow"])
            elif event.key == K_d:
                self._player.call_animal("dog", self._animal_sprites_grouped_dict["dog"])
            elif event.key == K_f:
                self._player.call_animal("pig", self._animal_sprites_grouped_dict["pig"])
            elif event.key == K_g:
                self._player.call_animal("sheep", self._animal_sprites_grouped_dict["sheep"])

    def draw(self):

        #self.draw_bounding_boxes()
        # Remove old sprites from the background by redrawing those sections
        self._all_sprites.clear(self.screen, self.background)
        # Get the areas that are changed
        rectlist = self._all_sprites.draw(self.screen)
        # add bounding boxes (temp)
        #rectlist += [play_area, gate]
        #rectlist += [animal.rect.inflate(2, 2) for animal in self._animal_sprites]
        # Draw the changed parts of the screen
        pygame.display.update(rectlist)

    def redraw_whole_screen(self, start_sound=False):
        """
        Redaws the whole screen. This is used when the game is paused and it is supposed to be shown in the background
        of a menu.
        :param start_sound: Indicates whether the audio input and classification threads are started or not.
        :return: -
        """

        if start_sound:
            self.sound_effect_interface.start_threads()

        self.screen.blit(self.background, (0, 0))
        for sprite in self._all_sprites:
            if type(sprite) != Animal:
                sprite.dirty = 1

    def draw_bounding_boxes(self):
        pygame.draw.rect(self.screen, (255, 0, 0), play_area, 2)
        pygame.draw.rect(self.screen, (0, 255, 0), gate, 2)

        for animal in self._animal_sprites:
            pygame.draw.rect(self.screen, (255,0,0), animal.rect.inflate(2,2), 2)


