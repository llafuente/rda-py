import logging
import asyncio
import time

from .base import Base
from .automation import Automation
from .utils import hex_color_to_rgba, rgba_to_hex_color, rgb_to_hex_color, loop_until
from typing import TYPE_CHECKING, Union, Tuple
if TYPE_CHECKING:
    from .windowsearch import WindowSearch


class Window(Base):
    """
    Single window operations at OS level
    """
    #: back ref to automation
    automation: Automation

    @property
    def title(self) -> str:
        """
        Window title
        """
        return self.automation.ahk.win_get_title(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

    _pid: Union[int, None] = None

    @property
    def pid(self) -> Union[int, None]:
        """
        Process identifier (cached)
        """
        if self._pid is None:
            self._pid = self.automation.ahk.win_get_pid(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

        return self._pid

    __process:Union[str, None] = None

    @property
    def process(self) -> Union[str, None]:
        """
        The name of the process that owns the window (cached).
        """
        if (self.__process is None):
            self.__process = self.automation.ahk.win_get_process_name(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self.__process

    __path: Union[str, None] = None

    @property
    def path(self) -> Union[str, None]:
        """
        Full path and name of the process that owns the window (cached)
        """
        if (self.__path == None):
            self.__path = self.automation.ahk.win_get_process_path(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self.__path

    __classNN: Union[str, None] = None

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


    @property
    def minimized(self) -> bool:
        """
        Is window minimized?
        """
        return self.automation.ahk.win_get_minmax(title=f"ahk_id {self.hwnd}", detect_hidden_windows=True) == -1

    @property
    def restored(self) -> bool:
        """
        Is window restored ?
        """
        return self.automation.ahk.win_get_minmax(title=f"ahk_id {self.hwnd}", detect_hidden_windows=True) == 0

    @property
    def maximized(self) -> bool:
        """
        Is window maximized?
        """
        return self.automation.ahk.win_get_minmax(title=f"ahk_id {self.hwnd}", detect_hidden_windows=True) == 1



    #: Control parameter from ControlSend. See <RDA_KeyboardSendKeys>
    #:
    #: Only apply when <RDA_Automation.inputMode> is background
    default_background_control: Union[str, None] = None # TODO if possible! empty string

    def __init__(self, automation: Automation, hwnd: str):
        #: Automation config (back pointer)
        self.automation = automation
        #: window handle identifier
        self.hwnd = hwnd

    def __str__(self):
        return f'Window(hwnd = {self.hwnd})'

    def __repr__(self):
        return self.__str__()

    def set_opaque(self) -> 'Window':
        """
        Set window opaque (remove transparency)

        :return: Window for chaining
        """
        self._debug(f"({locals()})")
        self.automation.ahk.win_set_transparent('Off', title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self


    async def wait_until_title_change_from(self, previous_title: Union[str, None] = None, timeout: int = -1, delay: int = -1) -> str:
        """
        Waits until title change from the giving one with timeout and error handling

        :param previous_title: Previous title to compare against. Empty to trigger on the first change.
        :param timeout: Maximum time in milliseconds to wait (default -1 for Automation.TIMEOUT)
        :param delay: Time in milliseconds between checks (default -1 for Automation.DELAY)

        :return: current title
        """
        # Initialize with empty or provided previous title
        if not previous_title:
            previous_title = self.title

        # Override defaults?
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

        raise RuntimeError("unreachable code") # pragma: no cover

    async def wait_until_title_change_to(self, new_title: Union[str, None] = None, timeout: int = -1, delay: int = -1) -> str:
        """
        Waits until title change from the giving one with timeout and error handling

        :param new_title: New title to compare against.
        :param timeout: Maximum time in milliseconds to wait (default -1 for no timeout)
        :param delay: Time in milliseconds between checks (default -1 for Automation.DELAY)

        :return: current title
        """
        # Use instance's automation settings if available
        timeout = timeout if timeout != -1 else self.automation.TIMEOUT
        delay = delay if delay != -1 else self.automation.DELAY

        self.debug(locals())

        max_ms = time.time_ns() + timeout * 1_000_000

        while True:
            current_title = self.title

            if current_title == new_title:
                self._debug(f"Title changed to '{current_title}'")
                return current_title

            if time.time_ns() > max_ms:
                raise TimeoutError(f"Timeout after {timeout}ms waiting for title change")

            await asyncio.sleep(delay / 1000)  # Convert delay from ms to seconds

        raise RuntimeError("unreachable code") # pragma: no cover

    def close(self, timeout: int = -1, unable_to_close_exception: Union[Exception, None] = Exception("Could not close window")) -> 'Window':
        """
        Closes window and wait until the specified window does not exist.

        :param timeout: Timeout in miliseconds
        :param unable_to_close_exception: Exception to throw if we are unable to close

        :return: Window for chaining
        """
        timeout = timeout if timeout != -1 else self.automation.TIMEOUT
        self._debug(f"({locals()})")

        self.automation.ahk.win_close(title=f"ahk_id {self.hwnd}", seconds_to_wait=timeout/1000, detect_hidden_windows = True)
        if self.is_alive() and unable_to_close_exception is not None:
            raise unable_to_close_exception

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
        # TODO REVIEW need to add GetAncestor -> check is activated ?
        # winHwnd := DllCall("User32\GetAncestor", "Ptr", hwnd, "UInt", 2, "Ptr") ;GA_ROOT := 2
        # hwnd2 := DllCall("User32\GetForegroundWindow")

        minimized = self.minimized
        self.automation.ahk.win_activate(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        # window "opening" animation time
        if minimized:
            self.sleep(self.automation.WINDOW_OPEN_ANIMATION)

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

    def move2(self, x: int, y: int) -> 'Window':
        """
        Alias of set_position
        """
        return self.set_position(x, y)

    def get_position(self) -> Tuple[int, int]:
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
        self.automation.action_performed()

        return self

    def get_size(self) -> Tuple[int, int]:
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
        self.automation.action_performed()

        return self

    def resize(self, width: int, height: int) -> 'Window':
        """
        Alias of set_size
        """
        return self.set_size(width, height)

    def get_region(self) -> Tuple[int, int, int, int]:
        """
        Get window screen position and size as (x, y, width, height)

        :return: (x, y, width, height)
        """
        pos = self.automation.ahk.win_get_position(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)

        self._debug(f"<-- ({pos})")
        return pos.x, pos.y, pos.width, pos.height

    def get_rectangle(self) -> Tuple[int, int, int, int]:
        """
        Alias of get_region but return (left, top, right, bottom)
        """
        x, y, width, height = self.get_region()
        return x, y, x + width, y + height

    def minimize(self) -> 'Window':
        """
        Minimizes the window.

        :return: Window for chaining
        """
        self._debug(f"({locals()})")
        self.automation.ahk.win_minimize(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self

    def restore(self) -> 'Window':
        """
        Restores the window.

        :return: Window for chaining
        """
        self._debug(f"({locals()})")
        self.automation.ahk.win_restore(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self

    def maximize(self) -> 'Window':
        """
        Maximizes the window.

        :return: Window for chaining
        """
        self._debug(f"({locals()})")
        self.automation.ahk.win_maximize(title=f"ahk_id {self.hwnd}", detect_hidden_windows = True)
        return self

    #
    # mouse operations
    #

    def mouse_move2(self, x: int, y: int) -> 'Window':
        """
        Moves mouse cursor to a position given window position

        :param x: window x coordinate
        :param y: window x coordinate

        :return: Window for chaining
        """
        mouse = self.automation.mouse()
        self.activate()
        x2, y2 = self.get_position()
        mouse.move_to2(x + x2, y + y2)
        return self

    def click2(self, x: int, y: int) -> 'Window':
        """
        Performs a left click at given window position.

        :param x: window x coordinate
        :param y: window x coordinate

        :return: Window for chaining
        """
        logging.debug(f'click2({x}, {y})')

        mouse = self.automation.mouse()
        self.activate()
        x2, y2 = self.get_position()
        mouse.click2(x + x2, y + y2)
        return self

    def right_click2(self, x: int, y: int) -> 'Window':
        """
        Performs a right click at given window position.

        :param x: window x coordinate
        :param y: window x coordinate

        :return: Window for chaining
        """
        logging.debug(f'right_click2({x}, {y})')

        mouse = self.automation.mouse()
        self.activate()
        x2, y2 = self.get_position()
        mouse.right_click2(x + x2, y + y2)
        return self

    def double_click2(self, x: int, y: int) -> 'Window':
        """
        Performs a left double click at given window position.

        :param x: window x coordinate
        :param y: window x coordinate

        :return: Window for chaining
        """
        logging.debug(f'double_click2({x}, {y})')

        mouse = self.automation.mouse()
        self.activate()
        x2, y2 = self.get_position()
        mouse.double_click2(x + x2, y + y2)
        return self

    #
    # windows
    #
    def get_child(self, search_obj: Union['WindowSearch', dict], include_hidden = False, not_found_exception: Union[Exception, None] = Exception("Child window not found")) -> 'Window':
        """
            Retrieves a "single" child window that matches the specified search criteria.

        :param search_obj: Search criteria, either as a dictionary or a WindowSearch object
        :param include_hidden: Whether to include hidden windows in the search (default: False)

        :raise: Window not found
        :raise: Multiple windows found

        :return: The child window
        """
        # Convert dictionary to WindowSearch if needed
        if isinstance(search_obj, dict):
            from .windowsearch import WindowSearch
            search_obj = WindowSearch(self.automation, **search_obj)

        if search_obj.pid is not None:
            raise ValueError("pid is not allowed in search_obj")
        search_obj.pid = self.pid

        rwins = self.automation.windows()._find(search_obj, include_hidden)
        self.debug(locals(), f'Found {len(rwins)} windows')

        if not rwins:
            if not_found_exception is not None:
                raise not_found_exception
            return None

        if len(rwins) > 1:
            raise RuntimeError("Multiple windows found")

        return rwins[0]

    def wait_child(self, search_obj: Union['WindowSearch', dict], include_hidden = False, timeout: int = -1, delay: int = -1, not_found_exception: Union[Exception, None] = Exception("Child window not found")) -> 'Window':
        """
        Waits until a child window that matches the specified search criteria is found.

        :param search_obj: Search criteria, either as a dictionary or a WindowSearch object
        :param include_hidden: Whether to include hidden windows in the search (default: False)
        :param timeout: Maximum time in milliseconds to wait (default -1 for Automation.TIMEOUT)
        :param delay: Time in milliseconds between checks (default -1 for Automation.DELAY)
        :param not_found_exception: Exception to raise if the child window is not found within the timeout

        :return: The child window
        """
        # Convert dictionary to WindowSearch if needed
        if isinstance(search_obj, dict):
            from .windowsearch import WindowSearch
            search_obj = WindowSearch(self.automation, **search_obj)

        if search_obj.pid is not None:
            raise ValueError("pid is not allowed in search_obj")

        search_obj.pid = self.pid

        def check():
            wins = self.automation.windows()._find(search_obj, include_hidden)
            if not wins or len(wins) > 1:
                return True, None

            self.debug(locals(), f'Found {len(wins)} windows')
            return False, wins[0]

        return loop_until(check,
            timeout if timeout != -1 else self.automation.TIMEOUT,
            delay if delay != -1 else self.automation.DELAY,
            not_found_exception)
    #
    # keyboard
    #

    def type(self, text: str) -> 'Window':
        """
        Sends given text (literally) as keystrokes

        :remarks:
          This method can disclosure information, use <Keyboard.send_password>

        :remarks:
          use Raw mode: https://www.autohotkey.com/docs/v1/lib/Send.htm#Raw

        :param text: text.

        :return: Window for chaining
        """
        self.automation.keyboard().type(text, self.hwnd, self.default_background_control)
        return self


    def type_password(self, password: str) -> 'Window':
        """
        Sends given password (literally) as keystrokes

        :remarks:
          This method do not disclosure information, just log the length of the password

        :remarks:
          use Raw mode: https://www.autohotkey.com/docs/v1/lib/Send.htm#Raw

        :param password: password.

        :return: Window for chaining
        """
        self.automation.keyboard().type_password(password, self.hwnd, self.default_background_control)
        return self

    def send_keys(self, keys: str) -> 'Window':
        """
        Sends simulated keystrokes

        :remarks:
          This method can disclosure information, use <Keyboard.send_password>

        :param keys: keys.

        :return: Window for chaining
        """
        self.automation.keyboard().send_keys(keys, self.hwnd, self.default_background_control)
        return self

    def send_password(self, password: str) -> 'Window':
        """
        It's an alias of <Keyboard.sendKeys> but just log the length

        :remarks:
          This method do not disclosure information, just log the length of the password

        :param password: password.

        :return: Window for chaining
        """
        self.automation.keyboard().send_password(password, self.hwnd, self.default_background_control)
        return self


    #
    # pixel
    #

    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """
        Retrieves the color of the pixel at the specified X and Y coordinates.

        :param x: x window coordinate
        :param y: y window coordinate

        :remarks: (255, 255, 255, 255) Will be returned when workstation is locked.
        """
        x2, y2 = self.get_position()
        # TODO REVIEW locked workstation color in python is 0xFFFFFFFF
        color = hex_color_to_rgba(self.automation.ahk.pixel_get_color(x + x2, y + y2, coord_mode='Screen', rgb=True))
        logging.debug(f'Window.get_pixel_color({x}, {y}) <-- {color}')
        return color

    def find_pixel_color(self, x: int, y: int, witdh:int, height:int, rgb_color: Tuple[int, int, int], variation:int = 0, not_found_exception: Union[Exception, None] = Exception("pixel color not found")) -> Union[Tuple[int, int], None]:
        """
        Searches for a pixel of the specified color within a defined rectangular area of the window.

        :param x: x window coordinate
        :param y: y window coordinate
        :param width: region width
        :param height: region height
        :param rgb_color: color
        :param variation: color variation
        :param not_found_exception: exception raised if not found

        :return: pixel position
        """
        x2, y2 = self.get_position()
        search_region_start = (x+x2,y+y2)
        search_region_end = (x+x2+witdh,y+y2+height)
        color_str = rgb_to_hex_color(rgb_color[0], rgb_color[1], rgb_color[2])

        position = self.automation.ahk.pixel_search(search_region_start, search_region_end, color=color_str, variation=variation, coord_mode='Screen', rgb=True)

        if position is not None:
            position = (position[0]-x2, position[1]-y2)

        #logging.debug(f'find_pixel_color({x}, {y}, {witdh}, {height}, {rgb_color}) <-- {position}')
        logging.debug(f'find_pixel_color({search_region_start}, {search_region_end}, {color_str}) <-- {position}')

        if position is None and not_found_exception is not None:
            raise not_found_exception

        return position

    #
    # images
    #

    def get_image(self, image_path: str, variation: int = 0, not_found_exception: Union[Exception, None] = Exception("Image not found")) -> Tuple[int, int]:
        """
        Checks if the specified image is currently visible on the window.

        :param image_path: The file path of the image to search for.
        :param variation: The allowed color variation (0-255) when matching the image.

        :return: True if the image is found on the window, False otherwise.
        """
        self.set_opaque().activate()

        upper_bound = self.get_position()
        lower_bound = self.get_size()
        lower_bound = (lower_bound[0] + upper_bound[0], lower_bound[1] + upper_bound[1])

        self.debug(locals())

        # (image_path: str, upper_bound: Tuple[int | str, int | str] = (0, 0), lower_bound: Tuple[int | str, int | str] | None = None, *, color_variation: int | None = None, coord_mode: CoordModeRelativeTo | None = None, scale_height: int | None = None, scale_width: int | None = None, transparent: str | None = None, icon: int | None = None) -> (Coordinates | None)
        pos = self.automation.ahk.image_search(image_path, upper_bound, lower_bound, color_variation = variation, coord_mode = 'Screen')

        if pos == None and not_found_exception is not None:
            raise not_found_exception

        return pos

    def has_image(self, image_path: str, variation: int = 0) -> bool:
        """
        Checks if the specified image is currently visible on the window.

        :param image_path: The file path of the image to search for.
        :param variation: The allowed color variation (0-255) when matching the image.

        :return: True if the image is found on the window, False otherwise.
        """

        pos = self.get_image(image_path, variation, not_found_exception = None)
        return pos != None

    def wait_image_appear(self, image_path: str, variation: int = 0, not_found_exception: Union[Exception, None] = Exception("Image not found"), timeout: int = -1, delay: int = -1) -> Tuple[int, int]:
        """
        Waits until the specified image appears on the window.

        :param image_path: The file path of the image to search for.
        :param variation: The allowed color variation (0-255) when matching the image.
        :param not_found_exception: Exception to raise if the image is not found within the timeout
        :param timeout: Maximum time in milliseconds to wait (default -1 for Automation.TIMEOUT)
        :param delay: Time in milliseconds between checks (default -1 for Automation.DELAY)

        :return: The coordinates of the found image on the window.
        """

        # Override defaults?
        timeout = timeout if timeout != -1 else self.automation.TIMEOUT
        delay = delay if delay != -1 else self.automation.DELAY

        def check():
            pos = self.get_image(image_path, variation, None)
            if pos is None:
                return True, None
            return False, pos

        return loop_until(check,
            timeout,
            delay,
            not_found_exception)

    def wait_image_disappear(self, image_path: str, variation: int = 0, not_dissapear_exception: Union[Exception, None] = Exception("Image still present"), timeout: int = -1, delay: int = -1) -> bool:
        """
        Waits until the specified image disappears from the window.

        :param image_path: The file path of the image to search for.
        :param variation: The allowed color variation (0-255) when matching the image.
        :param not_dissapear_exception: Exception to raise if the image is still present within the timeout
        :param timeout: Maximum time in milliseconds to wait (default -1 for Automation.TIMEOUT)
        :param delay: Time in milliseconds between checks (default -1 for Automation.DELAY)

        :return: True if the image disappeared, False otherwise.
        """

        # Override defaults?
        timeout = timeout if timeout != -1 else self.automation.TIMEOUT
        delay = delay if delay != -1 else self.automation.DELAY

        def check():
            pos = self.get_image(image_path, variation, None)
            if pos is None:
                return False, True
            return True, False

        return loop_until(check,
            timeout,
            delay,
            not_dissapear_exception)

