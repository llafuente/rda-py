import logging
import time
from ahk import AHK

from .base import Base

# fix circular imports
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .window import Window
    from .mouse import Mouse
    from .windows import Windows
    from .keyboard import Keyboard

class Automation(Base):
    """
        Automation configuration and the library entry point.
    """
    ahk_executable_path: Union[str, None] = None
    #: AutoHotKey library
    ahk: AHK = None

    #: Default timeout, in milliseconds
    TIMEOUT: int = 60000

    #: Default delay, in milliseconds
    DELAY: int = 250

    #: Default highlight time, in milliseconds
    HIGHLIGHT_TIME: int = 1000

    #: Default wait time for opening window animation
    WINDOW_OPEN_ANIMATION: int = 500

    #: Delay between key strokes, in milliseconds.
    #:
    #: Use -1 for no delay at all and 0 for the smallest possible delay
    #:
    #: See: https://www.autohotkey.com/docs/commands/SetKeyDelay.htm
    key_delay: int = 100

    #: Certain games and other specialized applications may require a delay inside each keystroke; that is, after the press of the key
    #: but before its release.
    #:
    #: Specify -1 for no delay at all or 0 for the smallest possible delay (however, if the Play parameter is present, both 0 and -1 produce no delay).
    #:
    #: See: https://www.autohotkey.com/docs/commands/SetKeyDelay.htm
    press_duration: int = -1

    #: Configures how input is going to be sent
    #:
    #: Valid values:
    #:
    #: * interactive
    #:
    #: * background (non-interactive)
    input_mode: str = "interactive"

    #: Makes Send synonymous with SendInput or SendPlay rather than the
    #: default (SendEvent). Also makes Click and MouseMove/Click/Drag use the
    #: specified method.
    #:
    #: Valid values:
    #:
    #: * Event (*default*)
    #:
    #: * Input
    #:
    #: * InputThenPlay
    #:
    #: * Play
    #:
    #: See: https://www.autohotkey.com/docs/commands/SendMode.htm
    send_mode: str = "Event"

    #: Delay after each action performed by the library.
    #:
    #: This value allows you to adapt to performance degrade in long running
    #: applications and also helps you to slow down a bot to debug.
    #: NOTE: this also applies to mouse actions (mouse_delay is removed)
    action_delay: int = 100

    #: number - Default mouse movement speed
    #:
    #: See: https://www.autohotkey.com/docs/v1/lib/MouseMove.htm
    mouse_speed: int = 2

    #: Default image search sensibility. See "\*n (variation)" at https://www.autohotkey.com/docs/v1/lib/ImageSearch.htm#Parameters
    image_search_sensibility: int = 4

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.input_mode)}, {repr(self.key_delay)}, {repr(self.send_mode)}, {repr(self.action_delay)}, {repr(self.mouse_speed)}, {repr(self.image_search_sensibility)}, {repr(self.ahk_executable_path)})'

    def __init__(self,
                 input_mode:str = "interactive",
                 key_delay=50,
                 send_mode="Event",
                 action_delay=100,
                 mouse_speed=2,
                 image_search_sensibility=4,
                 ahk_executable_path: str = None):
        """
        Constructor to initialize all properties

        :param key_delay: Delay between key strokes, in milliseconds
        :param key_delay: Delay between key strokes, in milliseconds
        :param send_mode: Configures how input is going to be sent ("interactive" or "background")
        :param action_delay: Delay after each action performed by the library
        :param mouse_speed: Default mouse movement speed
        :param image_search_sensibility(number): see <Automation.imageSearchSensibility>
        :param ahk_executable_path: custom path AutoHotKey binary
        """
        self.ahk_executable_path = ahk_executable_path
        self.ahk = AHK(executable_path = ahk_executable_path)
        self.set_input_mode(input_mode)
        self.set_key_delay(key_delay)
        self.set_send_mode(send_mode)
        self.set_action_delay(action_delay)
        self.set_mouse_speed(mouse_speed)

        self.set_image_search_sensibility(image_search_sensibility)

    def set_input_mode(self, input_mode: str):
        """
        Sets the how input will be sent

        :param input_mode (str): <Automation.input_mode>
        """
        try:
            ["interactive", "background"].index(input_mode)
        except:
            raise ValueError(f"Invalid input mode: {input_mode}")
        self.input_mode = input_mode

        return self

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

        :param key_delay (int): Delay between key strokes, in milliseconds
        """
        self.key_delay = key_delay

    def set_send_mode(self, send_mode):
        """
        Makes Send synonymous with SendInput or SendPlay rather than the default (SendEvent).
        Also makes Click and MouseMove/Click/Drag use the specified method.

        :param send_mode (str): See <Automation.sendMode>
        """
        try:
            ["Event", "Input", "InputThenPlay", "Play"].index(send_mode)
        except:
            raise ValueError(f"Invalid send mode: {send_mode}")

        self.send_mode = send_mode

    def set_image_search_sensibility(self, image_search_sensibility):
        """
        Configures default image search sensibility

        :param image_search_sensibility (int): see <Automation.image_search_sensibility>
        """
        self.image_search_sensibility = image_search_sensibility

    def set_press_duration(self, press_duration):
        """
        Sets press duration.

        :param press_duration (int): see <Automation.press_duration>
        """
        self.press_duration = press_duration

    def windows(self) -> 'Windows':
        """
        Get operations over Windows at OS level
        :returns Windows
        """
        from .windows import Windows
        return Windows(self)

    def keyboard(self) -> 'Keyboard':
        from .keyboard import Keyboard
        return Keyboard(self)

    def mouse(self) -> 'Mouse':
        from .mouse import Mouse
        return Mouse(self)

    def window_from_hwnd(self, hwnd: Union[str, int]) -> 'Window':
        """
        Creates a Window given a window handle

        :param hwnd: Window handle identifier

        :return: Window instance
        """
        from .window import Window
        return Window(self, hwnd)

    def action_performed(self):
        time.sleep(self.action_delay / 1000)
