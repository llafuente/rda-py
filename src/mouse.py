import json
from typing import Union, List, Optional
from .automation import Automation
import ahk
import ctypes
import logging

def _get_cursor_name():
    # Windows-specific way to get current cursor name
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return "Unknown"
        hcur = ctypes.windll.user32.GetCursor()
        if not hcur:
            return "Unknown"
        # Use GetCursorInfo (requires more code, skipping for simplicity)
        # Returning a fallback based on default cursor
        cur_name = {10042: "Arrow", 10095: "IBeam", 10096: "Wait",
                    10097: "Crosshair", 10098: "AppStarting",
                    10099: "Help", 10100: "SizeAll", 10101: "SizeNESW",
                    10102: "SizeNS", 10103: "SizeNWSE", 10104: "SizeWE",
                    10105: "UpArrow", 10106: "No", 10107: "Hand"}  # typical IDs
        return cur_name.get(hcur, "Unknown")
    except Exception:
        return "Unknown"

# === End Unknown Stubs ===

class ScreenPosition:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def equal(self, other) -> bool:
        if not isinstance(other, ScreenPosition):
            return False
        return self.x == other.x and self.y == other.y

    def toString(self) -> str:
        return f"({self.x}, {self.y})"


class Mouse:
    """
    Mouse operations at OS level
    """

    #: back ref to automation
    automation = None

    def __init__(self, automation: Automation):
        assert automation is not None, f"{self.__class__.__name__}(): automation is null"
        self.automation = automation

    def click2(self, x: int|None = None, y: int|None = None) -> "Mouse":
        """
        Performs a left click at given screen position.

        :param x: screen x coordinate
        :param y: screen x coordinate

        :return: Mouse for chaining
        """
        logging.debug(f'click2({x}, {y})')
        self.automation.ahk.click(x, y, button='L', click_count=1, coord_mode='Screen', send_mode=self.automation.send_mode)
        self.automation.action_performed()
        return self

    def right_click2(self, x: int = 9999, y: int = 9999) -> "Mouse":
        """
        Performs a right click at given screen position.

        :param x: screen x coordinate
        :param y: screen x coordinate

        :return: Mouse for chaining
        """
        logging.debug(f'right_click2({x}, {y})')
        self.automation.ahk.click(x, y, button='R', click_count=1, coord_mode='Screen', send_mode=self.automation.send_mode)
        self.automation.action_performed()
        return self

    def double_click2(self, x: int = 9999, y: int = 9999) -> "Mouse":
        """
        Performs a left double click at given screen position.

        :param x: screen x coordinate
        :param y: screen x coordinate

        :return: Mouse for chaining
        """
        logging.debug(f'double_click2({x}, {y})')
        self.automation.ahk.click(x, y, button='L', click_count=2, coord_mode='Screen', send_mode=self.automation.send_mode)
        self.automation.action_performed()
        return self

    def move_rel2(self, x: int, y: int) -> "Mouse":
        """
        Moves mouse cursor to a position relative to current position

        :param x: screen x coordinate
        :param y: screen x coordinate

        :return: Mouse for chaining
        """
        logging.debug(f'move_rel2({x}, {y})')
        if (self.automation.input_mode == 'background'):
            logging.warning("mouse move is not possible in background mode, use interactive instead")

        self.automation.ahk.mouse_move(x, y, speed=self.automation.mouse_speed, relative=True, send_mode=self.automation.send_mode, coord_mode='Relative')
        self.automation.action_performed()
        return self

    def move_to2(self, x: int, y: int) -> "Mouse":
        """
        Moves mouse cursor to a position given screen position

        :param x: screen x coordinate
        :param y: screen x coordinate

        :return: Mouse for chaining
        """
        logging.debug(f'move_to2({x}, {y})')
        if (self.automation.input_mode == 'background'):
            logging.warning("mouse move is not possible in background mode, use interactive instead")

        self.automation.ahk.mouse_move(x, y, speed=self.automation.mouse_speed, relative=False, send_mode=self.automation.send_mode, coord_mode='Screen')
        self.automation.action_performed()
        return self

    def get(self) -> (int, int):
        """
        Retrieves the current mouse position

        :return: mouse position
        """
        p = self.automation.ahk.get_mouse_position(coord_mode='Screen')
        logging.debug(locals())
        return p

    def get_position(self) -> (int, int):
        """
        Retrieves the current mouse position

        :return: mouse position
        """
        return self.get()

    def get_cursor(self) -> str:
        """
        Retrieves current cursor name

        :remarks: unkown if cannot be determined

        :return: cursor name
        """
        cursor_name = _get_cursor_name()
        logging.debug(locals())
        return cursor_name

    def is_cursor(self, list_or_name: Union[str, List[str]]) -> bool:
        """
        Checks if current cursor is contained in the given list

        :return: cursor name
        """
        # arrayize
        list = [list_or_name] if isinstance(list_or_name, str) else list_or_name
        try:
            logging.debug(f"isCursor <-- {list.index(self.getCursor())}")
            return True
        except:
            return False

    def wait_cursor(self,
                   list_or_name: Union[str, List[str]],
                   minimum_time: int = 500,
                   timeout: int = -1,
                   delay: int = -1) -> "Mouse":
        # TODO
        return self