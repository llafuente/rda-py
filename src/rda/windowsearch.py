import re

from .automation import Automation
from .window import Window
from .utils import loop_until
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
    #: Process id full match
    pid: Union[int, None] = None

    def __init__(self, automation: Automation, title = None, process= None, classNN= None, path= None, pid = None):
        self.automation = automation
        self.title = title
        self.process = process
        self.classNN = classNN
        self.path = path
        self.pid = pid

    def __str__(self):
        props = []
        if self.title is not None:
            props.append(f"title = {self.title}")
        if self.process is not None:
            props.append(f"process = {self.process}")
        if self.classNN is not None:
            props.append(f"classNN = {self.classNN}")
        if self.path is not None:
            props.append(f"path = {self.path}")
        if self.pid is not None:
            props.append(f"pid = {self.pid}")
        return f'WindowSearch({", ".join(props)})'

    def __repr__(self):
        return self.__str__()

    def _is_match(self, win: Window) -> bool:

        if self.title is not None:
            if isinstance(self.title, re.Pattern):
                if not self.title.match(win.title):
                    return False
            else:
                try:
                    win.title.lower().index(self.title.lower())
                except:
                    return False

        if self.classNN is not None:
            if isinstance(self.classNN, re.Pattern):
                if not self.classNN.match(win.classNN):
                    return False
            else:
                try:
                    win.classNN.lower().index(self.classNN.lower())
                except:
                    return False


        if self.path is not None:
            if isinstance(self.path, re.Pattern):
                if not self.path.match(win.path):
                    return False
            else:
                try:
                    win.path.lower().index(self.path.lower())
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

        if self.pid is not None:
            if self.pid != win.pid:
                return False

        return True


    def is_match(self, win: Window) -> bool:
        """
        Tests if given object match the current window.

        Match is case insensitive.
        """
        b = self._is_match(win)
        self.debug(locals(), b)
        return b

    def wait_until_match(self, win: Window, timeout_ms: int = -1, delay_ms: int = -1, timeout_exception=Exception("wait_until_match timeout")) -> bool:
        """
        Waits if given object match the current window.

        Match is case insensitive.
        """
        timeout_ms = timeout_ms if timeout_ms != -1 else self.automation.TIMEOUT
        delay_ms = delay_ms if delay_ms != -1 else self.automation.DELAY


        self._debug(f"({locals()})")

        def check():
            b = self.is_match(win)
            return not b,b

        return loop_until(check, timeout_ms, delay_ms, timeout_exception)