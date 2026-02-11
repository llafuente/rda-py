import re
import time
import pytest
import pytest_mock
import unittest
import logging
from src.window import Window
from src.windows import Windows
from src.windowsearch import WindowSearch
from src.automation import Automation
import asyncio
from .timer import Timer
from .utils import start

# Create a TestCase instance
t = unittest.TestCase()

@pytest.fixture
def automation() -> Automation:
    return Automation()

@pytest.fixture
def windows(automation) -> Windows:
    return automation.windows()

def test_match_after_close(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows):
    win = start(automation, request, "notepad.exe")
    win.close()

    search = WindowSearch(automation, process = "xxx")
    t.assertFalse(search.is_match(win))

    with t.assertRaises(Exception) as cm:
        search.wait_until_match(win, timeout_ms = 500)
    t.assertEqual(str(cm.exception), "wait_until_match timeout")

    search.process = "notepad.exe"
    t.assertTrue(search.wait_until_match(win, timeout_ms = 500))

    # careful! cached
    t.assertIsNotNone(win.process)

    # remove cache
    setattr(win, "_Window__process", None) # python nonsense!!!!
    t.assertIsNone(win.process)

    # same error if no existed ever
    win.hwnd = "0xFFFFFFFF"
    setattr(win, "_Window__process", None) # python nonsense!!!!
    t.assertIsNone(win.process)
