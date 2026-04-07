import json
from typing import Union, List, Optional
from unicodedata import name
from .automation import Automation
from .base import Base
import ahk
import ctypes
import logging

"""
Not working
def get_cursor_id2() -> int:
    # GetCursor returns a handle to the current cursor
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getcursor
    return ctypes.windll.user32.GetCursor()
"""
# get cursor id using getcursorinfo
def get_cursor_id() -> int:
    class CURSORINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_ulong),
                    ("flags", ctypes.c_ulong),
                    ("hCursor", ctypes.c_void_p),
                    ("ptScreenPos", ctypes.wintypes.POINT)]

    ci = CURSORINFO()
    ci.cbSize = ctypes.sizeof(CURSORINFO)
    if ctypes.windll.user32.GetCursorInfo(ctypes.byref(ci)):
        return ci.hCursor
    else: # pragma: no cover
        raise Exception("GetCursorInfo failed")

class Mouse(Base):
    """
    Mouse operations at OS level
    """

    #: back ref to automation
    automation: Automation

    def __init__(self, automation: Automation):
        assert automation is not None, f"{self.__class__.__name__}(): automation is null"
        self.automation = automation

    def click2(self, x: Union[int, None] = None, y: Union[int, None] = None) -> "Mouse":
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

    def right_click2(self, x: Union[int, None] = None, y: Union[int, None] = None) -> "Mouse":
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

    def double_click2(self, x: Union[int, None] = None, y: Union[int, None] = None) -> "Mouse":
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

    def move_rel2(self, x: Union[int, None] = None, y: Union[int, None] = None) -> "Mouse":
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

    def move_to2(self, x: Union[int, None] = None, y: Union[int, None] = None) -> "Mouse":
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

    def get(self) -> tuple[int, int]:
        """
        Retrieves the current mouse position

        :return: mouse position
        """
        p = self.automation.ahk.get_mouse_position(coord_mode='Screen')
        logging.debug(locals())
        return p

    def get_position(self) -> tuple[int, int]:
        """
        Retrieves the current mouse position

        :return: mouse position
        """
        return self.get()

    def get_cursor_id(self) -> int:
        """
        Retrieves current cursor id

        :remarks: unkown if cannot be determined

        :return: cursor id
        """
        cursor_id = get_cursor_id()
        self.debug(locals(), cursor_id)
        return cursor_id

    def get_cursor(self) -> str:
        """
        Retrieves current cursor name

        :remarks: unkown if cannot be determined

        :return: cursor name
        """
        cursor_id = get_cursor_id()
        cursors = {
            32512: 'arrow',
            32513: 'ibeam',
            32514: 'wait',
            32515: 'cross',
            32516: 'uparrow',
            32517: 'size_nwse',
            32518: 'size_nesw',
            32519: 'size_we',
            32520: 'size_ns',
            32521: 'size_all',
            32522: 'no',
            32523: 'hand',
            32642: 'appstarting',
            32643: 'help',
            32644: 'working_in_background',
        }
        cursor_name = cursors.get(cursor_id, 'unknown')
        self.debug(locals(), f'cursor_id={cursor_id}, cursor_name={cursor_name}')
        return cursor_name