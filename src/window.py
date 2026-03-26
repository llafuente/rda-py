import asyncio
import time

from .base import Base
from .automation import Automation

class Window(Base):
    automation: Automation
    """
    Automation a window
    """
    @property
    def title(self) -> str:
        """
        Window title
        """
        return self.automation.ahk.win_get_title(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
    _pid: int|None = None

    @property
    def pid(self) -> int|None:
        """
        Process identifier (cached)
        """
        if (self._pid == None):
            self._pid = self.automation.ahk.win_get_pid(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self._pid

    __process:str|None = None
    @property
    def process(self) -> str|None:
        """
        The name of the process that owns the window (cached).
        """
        if (self.__process is None):
            self.__process = self.automation.ahk.win_get_process_name(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self.__process

    __path: str|None = None
    @property
    def path(self) -> str|None:
        """
        Full path and name of the process that owns the window (cached)
        """
        if (self.__path == None):
            self.__path = self.automation.ahk.win_get_process_path(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self.__path

    __classNN: str|None = None
    @property
    def classNN(self) -> str:
        """
        window's class name (cached)
        """
        if (self.__classNN == None):
            self.__classNN = self.automation.ahk.win_get_class(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self.__classNN

    @property
    def alive(self) -> str:
        """
        Alias of is_alive
        """
        return self.is_alive()


    #: Control parameter from ControlSend. See <RDA_KeyboardSendKeys>
    #:
    #: Only apply when <RDA_Automation.inputMode> is background
    defaultBackgroundControl: str|None = None # TODO if possible! empty string

    def __init__(self, automation: Automation, hwnd: str):
        #: Automation config (back pointer)
        self.automation = automation
        #: window handle identifier
        self.hwnd = hwnd

    def __str__(self):
        return f'Window(hwnd = {self.hwnd})'

    def __repr__(self):
        return self.__str__()

    async def wait_until_title_change_from(self, previous_title: str|None = None, timeout: int = -1, delay: int = -1) -> str:
        """
        Waits until title change from the giving one with timeout and error handling

        :param previous_title (str): Previous title to compare against. Empty to trigger on the first change.
        :param timeout (int): Maximum time in milliseconds to wait (default -1 for no timeout)
        :param delay (int): Time in milliseconds between checks (default -1 for Automation.DELAY)

        :return: current title
        """
        # Initialize with empty or provided previous title
        if not previous_title:
            previous_title = self.title

        # Use instance's automation settings if available
        timeout = timeout if timeout != -1 else self.automation.TIMEOUT
        delay = delay if delay != -1 else self.automation.DELAY

        self._debug(f"({locals()})")

        max_ms = time.time_ns() + timeout * 1_000_000

        while True:
            current_title = self.title
            self._debug(f"{previous_title} / {current_title}")

            if current_title != previous_title:
                self._debug(f"Title changed from '{previous_title}' to '{current_title}'")
                return current_title

            if (time.time_ns() > max_ms):
                raise TimeoutError(f"Timeout after {timeout}ms waiting for title change")

            await asyncio.sleep(delay / 1000)  # Convert delay from ms to seconds

        raise RuntimeError("Unreachable code reached")

    async def wait_until_title_change_to(self, new_title: str|None = None, timeout: int = -1, delay: int = -1) -> str:
        """
        Waits until title change from the giving one with timeout and error handling

        :param new_title (str): New title to compare against.
        :param timeout (int): Maximum time in milliseconds to wait (default -1 for no timeout)
        :param delay (int): Time in milliseconds between checks (default -1 for Automation.DELAY)

        :return: current title
        """
        # Use instance's automation settings if available
        timeout = timeout if timeout != -1 else self.automation.TIMEOUT
        delay = delay if delay != -1 else self.automation.DELAY

        self._debug(f"({locals()}")

        max_ms = time.time_ns() + timeout * 1_000_000

        while True:
            current_title = self.title

            if current_title == new_title:
                self._debug(f"Title changed to '{current_title}'")
                return current_title

            if (time.time_ns() > max_ms):
                raise TimeoutError(f"Timeout after {timeout}ms waiting for title change")

            await asyncio.sleep(delay / 1000)  # Convert delay from ms to seconds

        raise RuntimeError("Unreachable code reached")

    def close(self, timeout: int = -1, not_close_exception: Exception|None = Exception("Could not close window")):
        """
        Closes window and wait until the specified window does not exist.
        """
        timeout = timeout if timeout != -1 else self.automation.TIMEOUT
        self._debug(f"({locals()})")

        self.automation.ahk.win_close(title=f"ahk_id {self.hwnd}", seconds_to_wait=timeout/1000, detect_hidden_windows = True)
        if self.is_alive() and not_close_exception is not None:
            raise not_close_exception

        return self

    def is_alive(self) -> bool:
        """
        Checks if the specified window exists, window can be hidden
        """
        x = self.automation.ahk.win_exists(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

        b = False if x == None else x
        self._debug(f"() <-- {b}")

        return b

    def is_dead(self):
        """
        alias of is_closed
        """
        return self.is_closed()

    def is_closed(self) -> bool:
        """
        Returns if the window is closed/destroyed/killed
        """
        return not self.is_alive()

    def activate(self) -> 'Window':
        """
        Activates / Bring to front / foreground window

        *windows knowledge*: It will switch to another Virtual Desktop if needed

        *windows knowledge*: It will fail if workstation is locked or Desktop/Session is non-interactive
        """
        self.automation.ahk.win_activate(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

        return self

    def is_foreground(self) -> bool:
        """
        Returns if the window is the foreground
        (the window with which the user is currently working)
        """
        return self.automation.windows().get_foreground().hwnd == self.hwnd

    def is_activated(self) -> bool:
        """
        Alias of <Window.is_foreground>
        """
        return self.is_foreground()

    def is_deactivated(self) -> bool:
        """
        Opposite of <Window.is_foreground>
        """
        return not self.is_foreground()

    def is_background(self) -> bool:
        """
        Opposite of <Window.is_foreground>
        """
        return not self.is_foreground()

    def set_title(self, new_title: str) -> 'Window':
        self._debug(f"({locals()})")
        self.automation.ahk.win_set_title(new_title, title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

        return self

    def move(self, x: int, y: int) -> 'Window':
        """
        Alias of set_position
        """
        return self.set_position(x, y)

    def get_position(self) -> (int, int):
        """
        Get window screen position
        """
        pos = self.automation.ahk.win_get_position(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

        self._debug(f"<-- ({pos})")
        return pos.x, pos.y

    def set_position(self, x: int, y: int) -> 'Window':
        """
        Changes the window position.

        :param x: x screen coordinate
        :param y: y screen coordinate
        """
        self._debug(f"({locals()})")
        self.automation.ahk.win_move(x=x, y=y, width=None, height=None, title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

        return self

    def get_size(self):
        """
        Get window screen width and height
        """
        pos = self.automation.ahk.win_get_position(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

        self._debug(f"<-- ({pos})")
        return pos.width, pos.height

    def set_size(self, width: int, height: int) -> 'Window':
        """
        Resizes the window.

        :param width: width
        :param height: height
        """
        self._debug(f"({locals()})")
        self.automation.ahk.win_move(x=None, y=None, width=width, height=height, title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

        return self

    def resize(self, width: int, height: int) -> 'Window':
        """
        Alias of set_resize
        """
        return self.set_size(width, height)