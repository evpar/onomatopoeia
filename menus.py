import pygame
from game_state import GameState
from help_functions import *
import settings


class MenuItem(pygame.font.Font, pygame.sprite.DirtySprite):
    def __init__(self, text, button_img, font=None, font_size=30, font_color=(255, 255, 255), pos_x=0, pos_y=0):

        pygame.sprite.DirtySprite.__init__(self)
        pygame.font.Font.__init__(self, font, font_size)

        self._button_image = button_img
        self.image = self._button_image
        self.rect = self.image.get_rect()
        self.text = text

        self.font_size = font_size
        self._text_color = font_color

        # create a button
        self.change_button_state(font_color)
        self.is_selected = False

    def set_position(self, x, y):
        self.rect.topleft = (x, y)

    def change_button_state(self, font_color, selected=False):
        """
        Change the color of the text on the button
        :param new_color: New color of the text (given as rgb tuple)
        :return: -
        """

        if selected:
            self.set_bold(True)
            self.set_underline(True)
        else:
            self.set_bold(False)
            self.set_underline(False)

        self.image = self._button_image.copy()
        label = self.render(self.text, True, font_color)

        pos_text_x = self.rect.width // 2 - label.get_rect().width // 2
        pos_text_y= self.rect.height // 2 - label.get_rect().height // 2
        self.image.blit(label, (pos_text_x, pos_text_y))

        self.dirty = 1

    def change_button_image(self, image):
        self._button_image = image
        self.rect.size = image.get_rect().size


class GameMenu(GameState):
    def __init__(self, items, button_image, text="", background=(0, 0, 0), font=None, font_size=40, font_color=(255, 255, 255)):
        super(GameMenu, self).__init__()

        self.background = background
        # background can be an image or a color
        if type(background) == tuple:
            self._bg_rect = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA, 32)
            self._bg_rect.fill(background)
        else:
            self._bg_rect = background

        self.previous_state_name = None

        # create buttons
        self._menu_items = []
        self._buttons = pygame.sprite.LayeredDirty()
        for index, item in enumerate(items):
            menu_item = MenuItem(item, button_image, font, font_size, font_color)

            # t_h: total height of text block
            self.t_h = len(items) * menu_item.rect.height
            pos_x = (self.screen.get_rect().width / 2) - (menu_item.rect.width / 2)
            pos_y = (self.screen.get_rect().height / 2) - (self.t_h / 2) + ((index * 2) + index * menu_item.rect.height)

            menu_item.set_position(pos_x, pos_y)
            self._menu_items.append(menu_item)
            self._buttons.add(menu_item)

        # Create text if provided
        self.text = text
        self.label = None

        if self.text is not "":
            self.set_text(self.text)

        self.start_new()


    def set_item_selection(self, key):
        """
        Marks the MenuItem chosen via up and down keys.
        """

        # Unmark the currently selected item
        self._menu_items[self._cur_item].change_button_state(BUTTON_TEXT_COLOR)

        # Change marked button
        if key == pygame.K_UP:
            self._cur_item = (self._cur_item - 1) % len(self._menu_items)
        elif key == pygame.K_DOWN:
            self._cur_item = (self._cur_item + 1) % len(self._menu_items)
        # Select/press the marked button
        elif key == pygame.K_RETURN:
            if self._menu_items[self._cur_item].text in ["Start", "New game"]:
                GameState.game_state_manager.set_state("level_1")

            elif self._menu_items[self._cur_item].text == "Quit":
                self.quit = True

            elif self._menu_items[self._cur_item].text == "Instructions":
                GameState.game_state_manager.push_state("instructions")

            elif self._menu_items[self._cur_item].text == "Continue":
                GameState.game_state_manager.pop_state()

            elif self._menu_items[self._cur_item].text == "Main menu":
                GameState.game_state_manager.empty_level_stack()
                GameState.game_state_manager.set_state("main_menu")
            elif self._menu_items[self._cur_item].text == "Next level":
                #previous_state = GameState.game_state_manager.get_previous_state_name()
                next_level_number = int(self.previous_state_name.split("_")[-1]) + 1
                next_level_name = "level_" + str(next_level_number)
                GameState.game_state_manager.set_state(next_level_name)

        # Change button to marked
        self._menu_items[self._cur_item].change_button_state(SELECTED_BUTTON_TEXT_COLOR, True)

    def get_event(self, event):

        # Change marked button
        if event.type == pygame.KEYDOWN:
            self.set_item_selection(event.key)

        elif event.type == pygame.QUIT:
            self.quit = True

    def start_new(self):

        # Update background (when returning from instructions this redraws the game state)
        if self.previous_state_name != None:
            GameState.game_state_manager.get_state(self.previous_state_name).redraw_whole_screen() #TODO: poistettiin False
            GameState.game_state_manager.get_state(self.previous_state_name).draw()

        # redraw background
        self.screen.blit(self._bg_rect, (0,0))

        # Draw text if given
        if self.text != "":
            self.screen.blit(self.label, (self.text_pos_x, self.text_pos_y))

        # reset buttons
        for button in self._menu_items:
            button.change_button_state(settings.BUTTON_TEXT_COLOR)
        # Select first button
        self._cur_item = 0
        self._menu_items[self._cur_item].change_button_state(settings.SELECTED_BUTTON_TEXT_COLOR, True)

        # redraw all buttons
        for button in self._buttons:
            button.dirty = 1

    def scale(self, button_image, background_image=None):

        # background can be an image or a color
        if background_image == None:
            self._bg_rect = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA, 32)
            self._bg_rect.fill(self.background)
        else:
            self._bg_rect = background_image
            self.redraw_whole_screen()

        # relocate buttons
        for button in self._buttons:
            button.change_button_image(button_image)
            button.change_button_state(BUTTON_TEXT_COLOR)
            relocate_rect(button.rect, settings.scale_factor)
            self._menu_items[self._cur_item].change_button_state(settings.SELECTED_BUTTON_TEXT_COLOR, True)
            #button.set_position(new_pos[0], new_pos[1])


    def redraw_whole_screen(self, start_thread=False):
        self.start_new()


    def set_text(self, text):
        self.text = text
        myfont = pygame.font.SysFont(None, 50)
        self.label = myfont.render(text, 1, (255, 255, 255))
        self.text_pos_y = (self.screen.get_rect().height / 2) - (self.t_h / 2) - self._menu_items[0].rect.height
        self.text_pos_x = self._menu_items[0].rect.center[0] - self.label.get_rect().width // 2

    def draw(self):

        # Get the changed areas and draw them on the screen
        rectlist = self._buttons.draw(self.screen)
        pygame.display.update(rectlist)

# ---------------------------------------------------------------------------------------------------------------------

class Instructions(GameState, pygame.font.Font):
    def __init__(self, image):
        super(Instructions, self).__init__()
        self.font_size = 30

        pygame.font.Font.__init__(self, None, self.font_size)
        self.font = pygame.font.SysFont("Tahoma", 20)
        black = (0, 0, 0)

        # TODO: PITKÄN TEKSTIN ESITTÄMINEN, pygame ei osaa renderöidä tekstin rivinvaihtoa...
        self.instructions_text = "Instructions"
        goal_text = ["Guide the animal the owner asks to the gate", "but be careful not to let wrong animals go there."]
        call_text = ["Animals can be controlled by calling them.", "Calling is done by 'imitating' the animal.",  "If an animal inside the call radius is called,",
                       "it turns towards the player."]
        call = "Calls:"

        controls_text = "Move the caretaker using arrow keys."
        calls = ['Cat: "MAU" or "MEOW"', 'Cow: "AMMUU" or "MOO', 'Dog: "HAU" or "WOOF"', 'Pig: "RÖH or "OINK"', 'Sheep: "BÄÄ" or "BAA"']
        pause_text = "Pause the game and open a menu by pressing Esc, Enter, or Space"
        self.texts = {"goal": self._create_texts(goal_text), "controls": self.font.render(controls_text, True, black),
                      "calls": self._create_texts(calls), "call_text": self._create_texts(call_text),
                      "call": self.render(call, True, black), "pause": self.render(pause_text, True, black) }

        self.button = MenuItem("Back", load_image(pygame, "button.png", 2))

        self.image = image

    def _create_texts(self, texts):
        return [self.font.render(text, True, (0,0,0)) for text in texts]

    def draw(self):

        self.screen.fill((204, 204, 255))

        self.text_y = 20

        # Text explaining the goal of the game
        for row in self.texts["goal"]:
            self.screen.blit(row, (20, self.text_y))
            self._line_break()

        # Player movement text
        self._blank_row()
        self.screen.blit(self.texts["controls"], (20, self.text_y))
        self._blank_row(2)

        # How to call animals text
        for row in self.texts["call_text"]:
            self.screen.blit(row, (20, self.text_y))
            self._line_break()

        # the word "Call:"
        self._blank_row()
        self.screen.blit(self.texts["call"], (20, self.text_y))
        self._line_break()

        # Onomatopoetic calls for the animals that can be used
        for call in self.texts["calls"]:
            self.screen.blit(call, (20, self.text_y))
            self._line_break()

        # Pause menu text
        self._blank_row()
        self.screen.blit(self.texts["pause"], (20, self.text_y))
        self._line_break()

        # Button for exiting the instructions screen
        self.screen.blit(self.button.image, (self.screen_rect.width // 2  - (self.button.rect.width / 2),
                                             (self.screen_rect.height - self.button.rect.height * 1.3)))
        # Add a picture of caretaker
        self.screen.blit(self.image, (500, 100))


    def _line_break(self, n=1):
        self.text_y += (25*n)

    def _blank_row(self, n=1):
        self.text_y += (18 * n)

    def get_event(self, event):

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            GameState.game_state_manager.pop_state()

        elif event.type == pygame.QUIT:
            self.quit = True

# ---------------------------------------------------------------------------------------------------------------------
