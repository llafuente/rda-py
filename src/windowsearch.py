import re

from .automation import Automation
from .window import Window
from .utils import call_repeat_while_return
from .base import Base
from typing import Union

class WindowSearch(Base):
    """
    Search window by partial(ci) match or regex of all non None properties
    """
    #: Automation config (back pointer)
    automation: Automation
    #: partial check or regex
    title: Union[str, re.Pattern, None] = None
    #: partial check or regex
    process: Union[str, re.Pattern, None] = None
    #: partial check or regex
    classNN: Union[str, re.Pattern, None] = None
    #: partial check or regex
    path: Union[str, re.Pattern, None] = None

    def __init__(self, automation: Automation, title = None, process= None, classNN= None, path= None):
        self.automation = automation
        self.title = title
        self.process = process
        self.classNN = classNN
        self.path = path

    def __str__(self):
        return f'WindowSearch({"" if self.title is None else f"title = {self.title},"}{"" if self.process is None else f"process = {self.process},"}{"" if self.classNN is None else f"classNN = {self.classNN}"}{"" if self.path is None else f"path = {self.path},"})'

    def __repr__(self):
        return self.__str__()

    def is_match(self, win: Window) -> bool:
        """
        Tests if given object match the current window.

        Match is case insensitive.
        """

        self._debug(f"({locals()})")

        if self.title is not None:
            if isinstance(self.title, re.Pattern):
                if not self.title.match(win.title):
                    return False
            else:
                try:
                    win.title.lower().index(self.title.lower())
                except:
                    return False

        if self.process is not None:
            p = win.process
            if p == None:
                return False

            if isinstance(self.process, re.Pattern):
                if not self.process.match(win.process):
                    return False
            else:
                try:
                    win.process.lower().index(self.process.lower())
                except:
                    return False

        return True

    def wait_until_match(self, win: Window, timeout_ms: int = -1, delay_ms: int = -1, timeout_exception=Exception("wait_until_match timeout")) -> bool:
        """
        Waits if given object match the current window.

        Match is case insensitive.
        """
        timeout_ms = timeout_ms if timeout_ms != -1 else self.automation.TIMEOUT
        delay_ms = delay_ms if delay_ms != -1 else self.automation.DELAY


        self._debug(f"({locals()})")
        return call_repeat_while_return(self.is_match, [win], {}, False, timeout_ms, delay_ms, timeout_exception)