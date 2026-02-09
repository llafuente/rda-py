import time
import logging
#import property from "property"

class Automation:
    """
        Automation configuration and the library entry point.
    """

    # Constants
    TIMEOUT = 60000
    """
    :type: int
    Default timeout, in milliseconds
    """
    DELAY = 250
    """
    :type: int
    Default delay, in milliseconds
    """
    HIGHLIGHT_TIME = 1000
    """
    :type: int
    Default highlight time, in milliseconds
    """

    # Properties
    key_delay = 50
    """
    :type: int
    number - Delay between key strokes, in milliseconds.

    Use -1 for no delay at all and 0 for the smallest possible delay

    See: https://www.autohotkey.com/docs/commands/SetKeyDelay.htm
    """
    press_duration = -1
    """
    :type: int
    Certain games and other specialized applications may require a
    delay inside       each keystroke; that is, after the press of the key
    but before its release.

    Specify -1 for no delay at all or 0 for the smallest possible delay
    (however, if the Play parameter is present, both 0 and -1 produce no delay).

    See: https://www.autohotkey.com/docs/commands/SetKeyDelay.htm
    """
    mouse_delay = 50
    """
    :type: int
    Delay between mouse strokes.

    Time in milliseconds.

    Specify -1 for no delay at all or 0 for the smallest possible delay

    See: https://www.autohotkey.com/docs/v1/lib/SetMouseDelay.htm
    """
    input_mode = "interactive"
    """
    :type: string
    string - Configures how input is going to be sent

    Valid values:

    * interactive

    * background (non-interactive)
    """
    send_mode = "Event"
    """
    :type: string
    string - Makes Send synonymous with SendInput or SendPlay rather than the
    default (SendEvent). Also makes Click and MouseMove/Click/Drag use the
    specified method.

    Valid values:

    * Event (*default*)

    * Input

    * InputThenPlay

    * Play

    See: https://www.autohotkey.com/docs/commands/SendMode.htm
    """
    action_delay = 100
    """
    :type: int
    Delay after each action performed by the library.

    This value allows you to adapt to performance degrade in long running
    applications and also helps you to slow down a bot to debug.
    """
    mouse_speed = 2
    """
    :type: int
    number - Default mouse movement speed

    See: https://www.autohotkey.com/docs/v1/lib/MouseMove.htm
    """
    blockInputInteractive = True
    """
    :type: boolean
    Blocks user input on interactive inputMode ?
    """
    blockInputBackground = False
    """
    :type: boolean
    Blocks user input on background inputMode ?
    """
    image_search_sensibility = 4
    """
    :type: int
    Default image search sensibility. See "*n (variation)" at https://www.autohotkey.com/docs/v1/lib/ImageSearch.htm#Parameters
    """

    @property
    def UIA(self):
        """
        Microsoft UI Automation (lazy initialization)
        """
        return None
    
    @property
    def JAB(self):
        """
        Java acess bridge (lazy initialization)
        """
        return None

    def __init__(self, key_delay=50, mouse_delay=50, send_mode="Event", action_delay=100, mouse_speed=2,
                 blockInputInteractive=True, blockInputBackground=False, image_search_sensibility=4):
        """
        Constructor to initialize all properties
        
        :param key_delay (int): Delay between key strokes, in milliseconds
        :param mouse_delay: int - Delay between mouse strokes. Time in milliseconds
        :param send_mode: str - Configures how input is going to be sent ("interactive" or "background")
        :param action_delay: int - Delay after each action performed by the library
        :param mouse_speed: int - Default mouse movement speed
        :param blockInputInteractive: bool - Blocks user input on interactive inputMode?
        :param blockInputBackground: bool - Blocks user input on background inputMode?
        :param image_search_sensibility: number - see <Automation.imageSearchSensibility>
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
        """
        Sets how much time we wait after performing an action: SendKeys/Click
        
        :param action_delay (int): Delay after each action performed by the library
        """
        logging.debug('set_action_delay', locals())

        self.action_delay= action_delay

    def set_mouse_speed(self, mouse_speed):
        """
        Sets mouse speed.

        :param mouse_speed (int): Speed of the mouse cursor
        """
        self.mouse_speed = mouse_speed

    def set_key_delay(self, key_delay):
        """
        Function to simulate SetKeyDelay in AutoHotkey

        :param key_delay: int - Delay between key strokes, in milliseconds
        """
        self.key_delay = key_delay

    def set_mouse_delay(self, mouse_delay):
        """
        Sets mouse delay.

        :param delay: int - mouse_delay
        """
        self.mouse_delay = mouse_delay

    def set_send_mode(self, send_mode):
        """
        Makes Send synonymous with SendInput or SendPlay rather than the default (SendEvent).
        Also makes Click and MouseMove/Click/Drag use the specified method.

        :param send_mode: str - see <Automation.sendMode>
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