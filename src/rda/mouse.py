import json
from typing import Union, List, Optional
from .automation import Automation
from .base import Base
import ahk
import ctypes
import logging

class Mouse(Base):
    """
    Mouse operations at OS level
    """

    #: back ref to automation
    automation = None

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