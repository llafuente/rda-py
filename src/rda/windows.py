from ahk import AHK
import logging

from .automation import Automation
from .window import Window
from .windowsearch import WindowSearch
from .base import Base
from typing import Union

class Windows(Base):
    def __init__(self, automation: Automation):
        self.automation = automation

    def get(self, include_hidden = False) -> list:
        """
        Retrieves all windows (hidden/visible)

        :param include_hidden: If True, include hidden windows. Defaults to False.

        :example
        >>> import Automation from rda
        >>> Automation().windows().get(include_hidden=True)
        """

        wins = self._get(include_hidden)
        self.debug(locals(), f"found {len(wins)} windows")

        return wins

    def _get(self, include_hidden) -> list:
        windows = self.automation.ahk.list_windows(detect_hidden_windows=include_hidden)

        r = []
        for win in windows:
            if win.id != None: #typechecker
                r.append(Window(self.automation, win.id))

        # self._debug(f"{r}")

        return r

    def get_foreground(self) -> Window:
        """
        Retrieves a window instance to the foreground window
        (the window with which the user is currently working).

        If workstation is locked, foreground cannot be determined

        :raise: Could not get foregound window
        """
        win = self.automation.ahk.get_active_window()
        self.debug(locals(), win.id if win is not None else None)

        if win is None:
            raise RuntimeError("Could not get foregound window")

        return Window(self.automation, win.id)

    def _find(self, search_object: WindowSearch, include_hidden):
        """Internal method to find windows matching search criteria."""
        result = []

        windows = self._get(include_hidden)

        for win in windows:
            if search_object.is_match(win):
                result.append(win)

        return result

    def find_one(self, search_obj: Union[WindowSearch, dict], include_hidden=False) -> Window:
        """
        Searches for a single window that matches the given search.

        :param searchObject: Object containing window properties to match
        :param include_hidden: Boolean indicating whether to search hidden windows

        :raise: Window not found
        :raise: Multiple windows found

        :return: The window object if exactly one match is found
        """

        # Convert dictionary to RDA_WindowSearch if needed
        if isinstance(search_obj, dict):
            search_obj = WindowSearch(self.automation, **search_obj)


        rwins = self._find(search_obj, include_hidden)
        self.debug(locals(), f'Found {len(rwins)} windows')

        if not rwins:
            raise RuntimeError("Window not found")

        if len(rwins) > 1:
            raise RuntimeError("Multiple windows found")

        return rwins[0]

    def find(self, search_obj: Union[WindowSearch, dict], include_hidden=False) -> list[Window]:
        """
        Searches for any window that matches the given search.

        :param searchObject: Object containing window properties to match
        :param include_hidden: Boolean indicating whether to search hidden windows

        :return: The window object if exactly one match is found
        """

        # Convert dictionary to RDA_WindowSearch if needed
        if isinstance(search_obj, dict):
            search_obj = WindowSearch(self.automation, **search_obj)

        self.debug(locals())

        rwins = self._find(search_obj, include_hidden)

        return rwins

    def minimize_all(self) -> "Windows":
        """
        Minimizes all windows

        :return: Windows for chaining
        """
        max = 100 # guard against infinite loop
        win = self.get_foreground()
        while True:
            win.minimize()
            win2 = self.get_foreground()
            if win.hwnd == win2.hwnd or --max <= 0:
                break # pragma no cover
            win = win2
        self.automation.action_performed()
        return self