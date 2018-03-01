import pygame


class GameStateManager():
    """
    The class is responsible for game states. For example changing a level is done using this class.
    """

    def __init__(self):
        # The preloaded states for the game
        self._states = {}
        # Stack for levels, used for example to implement pause
        self._level_stack = []
        self._current_state = None
        self._current_level_name = ""

    def add_state(self, level, level_name):
        """
        Add new level to the game
        :param level_name: string identifier for the level
        :param level: new level
        :return: -
        """

        self._states[level_name] = level

    def get_state(self, level_name):
        """
        Return the level associated with an identifier
        :param level_name: String identifier for a level
        :return: Level
        """
        try:
            return self._states[level_name]
        except KeyError:
            print("Error: no level with key", level_name)
            return None

    def set_state(self, level_name):
        """
        Go to another level
        :param level_name: String level identifier for the level to go to
        :return: -
        """

        self._current_level_name = level_name
        self._current_state = self._states[level_name]
        self._current_state.start_new()


    def push_state(self, level_name):
        """
        Push level to level stack
        :param level_name: Level identifier for the level to push to the stack
        :return: -
        """

        self._states[level_name].start_new()
        self._level_stack.append(self._current_level_name)
        self._current_state = self._states[level_name]
        self._current_level_name = level_name
        self._current_state.start_new()

    def pop_state(self):
        """
        Pop level from the level stack and go to the previous level
        :return: -
        """

        self._current_level_name = self._level_stack.pop()
        self._current_state = self._states[self._current_level_name]
        self._current_state.redraw_whole_screen(True)


    def get_current_state_name(self):
        """
        Return the name (identifier) for the current level
        :return: name of the level
        """
        return self._current_level_name

    def get_current_state(self):
        """
        Return current level
        :return: level
        """
        return self._current_state


    def empty_level_stack(self):
        """
        Remove all levels on level stack
        :return: -
        """
        self._level_stack.clear()


class GameState(object):
    """
    Parent class for individual game states to inherit from.
    """

    # static variable (takes care of state management)
    game_state_manager = GameStateManager()

    def __init__(self):
        self.quit = False
        self.screen_rect = pygame.display.get_surface().get_rect()
        self.font = pygame.font.Font(None, 24)
        self.redraw_background = False
        self.screen = pygame.display.get_surface()


    def start_new(self):
        """
        Called when a state resumes being active.
        """
        pass

    def get_event(self, event):
        """
        Handle a single event passed by the Game object.
        """
        if event.type == pygame.QUIT:
            self.quit = True

    def update(self, dt):
        """
        Update the state. Called by the Game object once
        per frame.

        dt: time since last frame
        """
        pass

    def draw(self):
        """
        Draw everything to the screen.
        """
        pass

    def redraw_whole_screen(self, start_thread=False):
        pass

    def give_scaled_graphics(self):
        pass
