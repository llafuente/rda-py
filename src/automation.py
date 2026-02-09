import time
import logging

class Automation:
    """
    Class: Automation
        Automation configuration and the library entry point.
    """

    # Constants
    TIMEOUT = 60000  # Default timeout, in milliseconds
    DELAY = 250      # Default delay, in milliseconds
    HIGHLIGHT_TIME = 1000  # Default highlight time, in milliseconds

    # Properties
    key_delay = 50  # Delay between key strokes, in milliseconds
    press_duration = -1  # Certain games and other specialized applications may require a delay inside each keystroke; that is, after the press of the key but before its release.
    mouse_delay = 50  # Delay between mouse strokes. Time in milliseconds
    input_mode = "interactive"  # Configures how input is going to be sent ("interactive" or "background")
    send_mode = "Event"  # Makes Send synonymous with SendInput or SendPlay rather than the default (SendEvent)
    action_delay = 100  # Delay after each action performed by the library
    mouse_speed = 2  # Default mouse movement speed

    blockInputInteractive = True  # Blocks user input on interactive inputMode?
    blockInputBackground = False  # Blocks user input on background inputMode?
    image_search_sensibility = 4  # Default image search sensibility

    def __init__(self, key_delay=50, mouse_delay=50, send_mode="Event", action_delay=100, mouse_speed=2,
                 blockInputInteractive=True, blockInputBackground=False, image_search_sensibility=4):
        """
        Constructor to initialize all properties
        :param key_delay: int - Delay between key strokes, in milliseconds
        :param mouse_delay: int - Delay between mouse strokes. Time in milliseconds
        :param send_mode: str - Configures how input is going to be sent ("interactive" or "background")
        :param action_delay: int - Delay after each action performed by the library
        :param mouse_speed: int - Default mouse movement speed
        :param blockInputInteractive: bool - Blocks user input on interactive inputMode?
        :param blockInputBackground: bool - Blocks user input on background inputMode?
        :param imageSearchSensibility: number - see <Automation.imageSearchSensibility>
        """
        self.set_key_delay(key_delay)
        self.set_mouse_delay(mouse_delay)
        self.set_send_mode(send_mode)
        self.set_action_delay(action_delay)
        self.set_mouse_speed(mouse_speed)

        #Automation.block_input(input_mode="interactive") if blockInputInteractive else Automation.unblock_input(input_mode="interactive")
        #Automation.block_input(input_mode="background") if blockInputBackground else Automation.unblock_input(input_mode="background")
        self.set_image_search_sensibility(image_search_sensibility)

    def set_action_delay(self, action_delay):
        logging.debug('set_action_delay', locals())

        self.action_delay= action_delay

    def set_mouse_speed(self, mouse_speed):
        self.mouse_speed = mouse_speed

    def set_key_delay(self, key_delay):
        """
        Function to simulate SetKeyDelay in AutoHotkey
        :param key_delay: int - Delay between key strokes, in milliseconds
        """
        self.key_delay = key_delay

    def set_mouse_delay(self, mouse_delay):
        """
        Function to simulate SetMouseDelay in AutoHotkey
        :param delay: int - Delay between mouse strokes. Time in milliseconds
        """
        self.mouse_delay = mouse_delay

    def set_send_mode(self, send_mode):
        """
        Function to simulate SendInput in AutoHotkey
        :param text: str - Text to be sent
        """
        if ["Event", "Input", "InputThenPlay", "Play"].index(send_mode) == -1:
            raise ValueError(f"Invalid send mode: {send_mode}")
        self.send_mode = send_mode

    def set_image_search_sensibility(self, image_search_sensibility):
        """
        Configures default image search sensibility
        :param image_search_sensibility: number - see <Automation.image_search_sensibility>
        :param confidence: float - Confidence level of the match (optional)
        """
        self.image_search_sensibility = image_search_sensibility

    @staticmethod
    def delay(delay):
        """
        Method to introduce a delay
        :param delay: int - Delay in milliseconds
        """
        time.sleep(delay / 1000)