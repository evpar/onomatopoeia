import sys
from game_level import *
from menus import *
from audio import SoundEventInterface
from pygame.transform import smoothscale
import settings


class Game(object):

    """
    A single instance of this class is responsible for
    managing which individual game state is active
    and keeping it updated. It also handles many of
    pygame's nuts and bolts (managing the event
    queue, framerate, updating the display, etc.).
    and its run method serves as the "game loop".
    https://gist.github.com/iminurnamez/8d51f5b40032f106a847
    """

    def __init__(self, screen):
        """
        Initialize the Game object.
        screen: the pygame display surface
        """

        self._screen = screen
        self.old_screen_size = None
        self._clock = pygame.time.Clock()
        self._fps = FPS
        self.original_files = {}
        self.scaled_files = {'animal_images': {}}
        self._mouse_down = False

        self._level_manager = GameState.game_state_manager

        # Class for handling audio input and classifying data
        self._sound_event_interface = SoundEventInterface()

        self.load_graphics()
        self.initialize_images()
        self._add_game_levels()

    def _add_game_levels(self):

        # Menus
        self._level_manager.add_state(
            GameMenu(('Start', 'Instructions', 'Quit'), self.scaled_files["button"],
                     background=self.scaled_files["menu_background"]), "main_menu")
        self._level_manager.add_state(Instructions(self.scaled_files["instructions"]), "instructions")
        self._level_manager.add_state(
            GameMenu(("Continue", "Instructions", "Main menu"), self.scaled_files["button"],
                     background=(0, 0, 130, 50)), "pause_menu")
        self._level_manager.add_state(
            GameMenu(("New game", "Main menu"), self.scaled_files["button"], "Game over!", background=(0, 0, 130, 50)),
            "game_ended_menu")
        self._level_manager.add_state(
            GameMenu(("Next level", "Main menu"), self.scaled_files["button"], "Level completed!",
                     background=(0, 0, 130, 50)), "next_level_menu")

        # Game levels
        self._level_manager.add_state(
            GameLevel(["dog", "cat"], self.scaled_files["background"],
                      self.scaled_files["player_images"],
                      self.scaled_files["animal_animations"],
                      self.scaled_files["bubble_images"],
                      self.scaled_files["owner_images"],
                      self.scaled_files["paw_images"],
                      self.scaled_files["fence_images"],
                      self.scaled_files["exclamation_image"],
                      self.scaled_files["gate_image"],
                      self.scaled_files["heard_image"],
                      self.scaled_files["shadow_image"],
                      self._sound_event_interface), "level_1")

        self._level_manager.add_state(
            GameLevel(["dog", "cat", "pig"], self.scaled_files["background"],
                      self.scaled_files["player_images"],
                      self.scaled_files["animal_animations"],
                      self.scaled_files["bubble_images"],
                      self.scaled_files["owner_images"],
                      self.scaled_files["paw_images"],
                      self.scaled_files["fence_images"],
                      self.scaled_files["exclamation_image"],
                      self.scaled_files["gate_image"],
                      self.scaled_files["heard_image"],
                      self.scaled_files["shadow_image"],
                      self._sound_event_interface), "level_2")

        self._level_manager.add_state(
            GameLevel(["dog", "cat", "pig", "sheep"], self.scaled_files["background"],
                      self.scaled_files["player_images"],
                      self.scaled_files["animal_animations"],
                      self.scaled_files["bubble_images"],
                      self.scaled_files["owner_images"],
                      self.scaled_files["paw_images"],
                      self.scaled_files["fence_images"],
                      self.scaled_files["exclamation_image"],
                      self.scaled_files["gate_image"],
                      self.scaled_files["heard_image"],
                      self.scaled_files["shadow_image"],
                      self._sound_event_interface), "level_3")

        self._level_manager.add_state(
            GameLevel(["dog", "cat", "pig", "sheep", "cow"], self.scaled_files["background"],
                      self.scaled_files["player_images"],
                      self.scaled_files["animal_animations"],
                      self.scaled_files["bubble_images"],
                      self.scaled_files["owner_images"],
                      self.scaled_files["paw_images"],
                      self.scaled_files["fence_images"],
                      self.scaled_files["exclamation_image"],
                      self.scaled_files["gate_image"],
                      self.scaled_files["heard_image"],
                      self.scaled_files["shadow_image"],
                      self._sound_event_interface), "level_4")

        self.set_screens_for_levels()

        # start game from main menu
        self._level_manager.set_state("main_menu")

    def set_screens_for_levels(self):
        # PURKKAA KOKO SYSTEEMI...

        self._levels = ["main_menu", "instructions", "pause_menu", "game_ended_menu", "next_level_menu", "level_1",
                        "level_2",
                        "level_3", "level_4"]
        for level in self._levels:
            self._level_manager.get_state(level).screen = self._screen

        if GameState.game_state_manager.get_current_state() is not None:
            GameState.game_state_manager.get_current_state().redraw_whole_screen()

    def load_graphics(self):
        # Load background
        self.original_files["menu_background"] = load_image(pygame, "bg_main_menu.png")
        self.original_files["background"] = load_image(pygame, "bg_grass.png")

        # Load animal images
        animals = ["cat", "cow", "dog", "pig", "sheep"]
        self.original_files["animal_images"] = {animal: load_image(pygame, animal + "_step0.png") for animal in animals}

        # Load animal animations
        self.original_files["animal_animations"] = {}
        for animal in animals:
            file_name = animal + "_step"
            self.original_files["animal_animations"][animal] = [load_image(pygame, file_name + str(i) + ".png") for i in
                                                                range(0, 8)]

        # Load player image
        self.original_files["player_images"] = [load_image(pygame, "caretaker_step" + str(i) + ".png") for i in range(0,7)]

        # Load bubble images
        bubble_files = ["speech_bubble_01.png", "speech_bubble_02.png", "thought_bubble.png"]
        self.original_files["bubble_images"] = [load_image(pygame, bubble_file) for bubble_file in bubble_files]

        # Load owner images
        owner_files = ["owner_1.png", "owner_2.png", "owner_3.png", "owner_4.png"]
        self.original_files["owner_images"] = [load_image(pygame, owner_file) for owner_file in owner_files]

        # Load UI images
        UI_paw_active = load_image(pygame, "paw_active.png")
        UI_paw_deactive = load_image(pygame, "paw_deactive.png")
        self.original_files["paw_images"] = [UI_paw_active, UI_paw_deactive]

        fence_image = load_image(pygame, "fence.png")
        fence_back_image = load_image(pygame, "fence_back.png")
        fence_left_image = load_image(pygame, "fence_left.png")
        fence_right_image = load_image(pygame, "fence_right.png")
        self.original_files["fence_images"] = [fence_image, fence_back_image, fence_left_image, fence_right_image]

        self.original_files["button"] = load_image(pygame, "button.png")
        self.original_files["gate_image"] = load_image(pygame, "gate.png")
        self.original_files["exclamation_image"] = load_image(pygame, "exclamation.png")
        self.original_files["heard_image"] = load_image(pygame, "question_mark.png")
        self.original_files["shadow_image"] = load_image(pygame, "shadow.png")

        self.original_files["instructions"] = load_image(pygame, "instructions_picture.png")

    def initialize_images(self):

        self.scaled_files = self.original_files.copy()

        # Animals
        self.scaled_files["animal_images"] = self.original_files["animal_images"].copy()
        for animal in self.original_files["animal_images"]:
            img = self.original_files["animal_images"][animal]
            self.scaled_files["animal_images"][animal] = smoothscale(img, (img.get_width() // 3, img.get_height() // 3))

        # Animal animations
        self.scaled_files["animal_animations"] = self.original_files["animal_animations"].copy()
        for animal in self.original_files["animal_animations"]:
            self.scaled_files["animal_animations"][animal] = [
                smoothscale(img, (img.get_width() // 3, img.get_height() // 3)) for img in
                self.scaled_files["animal_animations"][animal]]

        # Player
        self.scaled_files["player_images"] = [smoothscale(img, (img.get_width() // 3, img.get_height() // 3))
                                              for img in self.scaled_files["player_images"]]

        # bubbles
        self.scaled_files["bubble_images"] = [smoothscale(img, (img.get_width() // 3, img.get_height() // 3))
                                              for img in self.scaled_files["bubble_images"]]

        # Owners
        self.scaled_files["owner_images"] = [smoothscale(img, (img.get_width() // 3, img.get_height() // 3))
                                             for img in self.scaled_files["owner_images"]]

        self.scaled_files["paw_images"] = [smoothscale(img, (img.get_width() // 3, img.get_height() // 3))
                                           for img in self.scaled_files["paw_images"]]

        self.scaled_files["fence_images"] = [smoothscale(img, (img.get_width() // 3, img.get_height() // 3))
                                             for img in self.scaled_files["fence_images"]]

        img = self.scaled_files["instructions"]
        self.scaled_files["instructions"] = smoothscale(img, (img.get_width() // 2, img.get_height() // 2))

        img = self.scaled_files["button"]
        self.scaled_files["button"] = smoothscale(img, (img.get_width() // 2, img.get_height() // 2))

        img = self.scaled_files["exclamation_image"]
        self.scaled_files["exclamation_image"] = smoothscale(img, (img.get_width() // 3, img.get_height() // 3))

        img = self.scaled_files["gate_image"]
        self.scaled_files["gate_image"] = smoothscale(img, (img.get_width() // 3, img.get_height() // 3))

        img = self.scaled_files["heard_image"]
        self.scaled_files["heard_image"] = smoothscale(img, (img.get_width() // 3, img.get_height() // 3))
        
        img = self.scaled_files["shadow_image"]
        self.scaled_files["shadow_image"] = smoothscale(img, (img.get_width() // 3, img.get_height() // 3))

        img = self.scaled_files["background"]
        self.scaled_files["background"] = smoothscale(img, (img.get_width() // 2, img.get_height() // 2))

        img = self.scaled_files["menu_background"]
        self.scaled_files["menu_background"] = smoothscale(img, (img.get_width() // 2, img.get_height() // 2))

    def _scale_images(self, screen_size):

        for key in self.scaled_files:

            if type(self.scaled_files[key]) == dict:
                for animal in self.scaled_files[key]:
                    if type(self.scaled_files[key][animal]) == list:
                        self.scaled_files[key][animal] = [
                            smoothscale(self.original_files[key][animal][i], self._scaled_size(
                                self.scaled_files[key][animal][i].get_size(), screen_size)) for i in
                            range(len(self.scaled_files[key][animal]))]
                    else:
                        self.scaled_files[key][animal] = smoothscale(self.original_files[key][animal],
                                                                     self._scaled_size(
                                                                         self.scaled_files[key][animal].get_size(),
                                                                         screen_size))

            elif type(self.scaled_files[key]) == list:
                for i in range(len(self.scaled_files[key])):
                    self.scaled_files[key][i] = smoothscale(self.original_files[key][i],
                                                            self._scaled_size(self.scaled_files[key][i].get_size(),
                                                                              screen_size))
            else:
                self.scaled_files[key] = smoothscale(self.original_files[key],
                                                     self._scaled_size(self.scaled_files[key].get_size(), screen_size))

    def _scaled_size(self, image_size, screen_size):

        width = int((image_size[0] * screen_size[0]) / self.old_screen_size[0])
        height = int((image_size[1] * screen_size[1]) / self.old_screen_size[1])

        return width, height

    def event_loop(self):
        """Events are passed for handling to the current state."""

        for event in pygame.event.get():

            # If the window is resized
            if event.type == VIDEORESIZE:

                print(event.dict["size"])
                self.old_screen_size = self._screen.get_size()
                self._screen = pygame.display.set_mode(event.dict['size'], HWSURFACE | DOUBLEBUF | RESIZABLE)
                self.set_screens_for_levels()
                self._scale_images(event.dict['size'])

                # Calculate factor used to scale graphics
                position_scale_factor_x = event.dict['size'][0] / self.old_screen_size[0]
                position_scale_factor_y = event.dict['size'][1] / self.old_screen_size[1]
                settings.scale_factor = (position_scale_factor_x, position_scale_factor_y)

                # Update play area and screen size
                scale_rect(settings.gate, settings.scale_factor)
                scale_rect(settings.play_area, settings.scale_factor)
                settings.SCREEN_HEIGHT = event.dict["size"][1]
                settings.SCREEN_WIDTH = event.dict["size"][0]

                # Update fence positions
                settings.FENCE_RIGHT = relocate_point(settings.FENCE_RIGHT, settings.scale_factor)
                settings.FENCE_LEFT = relocate_point(settings.FENCE_LEFT, settings.scale_factor)
                settings.FENCE_FRONT = relocate_point(settings.FENCE_FRONT, settings.scale_factor)
                settings.FENCE_BACK = relocate_point(settings.FENCE_BACK, settings.scale_factor)

                # Update paw positions
                settings.PAW_POS = relocate_point(settings.PAW_POS, settings.scale_factor)

                # Update graphics for the game levels
                for level_name in self._levels:
                    state = GameState.game_state_manager.get_state(level_name)

                    if level_name in ["pause_menu", "game_ended_menu", "next_level_menu"]:
                        state.scale(self.scaled_files["button"])

                    elif "level" in level_name:
                        state.give_scaled_graphics(self.scaled_files["background"],
                                                   self.scaled_files["player_images"],
                                                   self.scaled_files["animal_animations"],
                                                   self.scaled_files["bubble_images"],
                                                   self.scaled_files["owner_images"], self.scaled_files["paw_images"],
                                                   self.scaled_files["fence_images"], self.scaled_files["gate_image"])

                    elif level_name == "main_menu":
                        state.scale(self.scaled_files["button"], self.scaled_files["menu_background"])

                GameState.game_state_manager.get_current_state().redraw_whole_screen()

            else:
                self._level_manager.get_current_state().get_event(event)


    def update(self, dt):
        """
        dt: milliseconds since last frame
        """

        if dt > 1000 / settings.FPS * 3:
            print("Warning: dt was", str(dt), ". Screen not updated.")
        else:
            self._level_manager.get_current_state().update(dt)

    def draw(self):
        self._level_manager.get_current_state().draw()

    def run(self):
        """
        Pretty much the entirety of the game's runtime will be
        spent inside this while loop.
        """
        while not self._level_manager.get_current_state().quit:
            dt = self._clock.tick(self._fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Animal daycare")
    # pygame.mouse.set_visible(0)  # hide mouse cursor
    # pygame.display.set_icon(kuva) # TODO: jos haluaa ikkunan ikonin vaihtaa niin näin
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)

    game = Game(screen)
    game.run()
    pygame.quit()
    sys.exit()
