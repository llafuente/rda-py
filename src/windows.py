from ahk import AHK

from .automation import Automation
from .window import Window
from .windowsearch import WindowSearch
from .base import Base

class Windows(Base):
    def __init__(self, automation: Automation):
        self.automation = automation

    def get(self, hidden = False) -> list:
        """
        Retrieves all windows

        :param hidden (bool): If True, include hidden windows. Defaults to False.

        :example
        >>> import Automation from rda
        >>> Automation().windows().get(hidden=True)
        """

        self._debug(f"({locals()})")
        wins = self._get(hidden)
        self._debug(f"<-- found {len(wins)} windows")

        return wins

    def _get(self, hidden) -> list:
        windows = self.automation.ahk.list_windows(detect_hidden_windows=hidden)

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
        """
        win = self.automation.ahk.get_active_window()
        if win is None:
            raise Exception("Could not get foregound window")
        return Window(self.automation, win.id)

    def _find(self, search_object: WindowSearch, hidden):
        """Internal method to find windows matching search criteria."""
        result = []

        self._debug(search_object)

        windows = self._get(hidden)

        for win in windows:
            if search_object.is_match(win):
                result.append(win)

        return result

    def find_one(self, search_obj: WindowSearch|dict, hidden=False) -> Window:
        """
        Searches for a single window that matches the given properties.

        Parameters:
        - searchObject: Object containing window properties to match
        - hidden: Boolean indicating whether to search hidden windows

        Returns:
        The window object if exactly one match is found

        Throws:
        Exception with "Window not found" or "Multiple windows found"
        """

        # Convert dictionary to RDA_WindowSearch if needed
        if isinstance(search_obj, dict):
            search_obj["automation"] = self.automation
            search_obj = WindowSearch(**search_obj)

        self._debug(f"({locals()})")

        rwins = self._find(search_obj, hidden)

        if not rwins:
            raise Exception("Window not found")

        if len(rwins) > 1:
            raise Exception("Multiple windows found")

        return rwins[0]