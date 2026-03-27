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
from src.mouse import Mouse
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

@pytest.fixture
def mouse(automation) -> Mouse:
    return automation.mouse()

def test_window_match_after_close(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows):
    win = start(automation, request, "notepad.exe")
    win.activate()
    t.assertEqual(win.is_alive(), not win.is_dead())
    t.assertEqual(win.is_alive(), not win.is_closed())
    t.assertEqual(win.is_foreground(), win.is_activated())
    t.assertEqual(win.is_background(), win.is_deactivated())

    win.move(0, 0)
    t.assertEqual(win.get_position(), (0,0))

    win.move(50, 50)
    t.assertEqual(win.get_position(), (50,50))

    win.resize(1024, 768)
    t.assertEqual(win.get_size(), (1024, 768))

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


def test_window_mouse(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows, mouse: Mouse):
    win = start(automation, request, "notepad.exe")
    win.resize(800, 600)

    for i in range(10):

        win.move(50*i,50*i)
        win.mouse_move2(100, 100)
        t.assertEqual(mouse.get(), (50*i+100,50*i+100))
    win.right_click2(200,200)


def test_window_keyboard(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows, mouse: Mouse):
    win = start(automation, request, "notepad.exe")
    win.resize(800, 600)
    win.move(0,0)
    win.send_keys("{CTRL down}e{CTRL up}{BACKSPACE}")
    win.type("Hello world!")
    win.send_keys("{CTRL down}ec{CTRL up}")
    t.assertEqual(automation.ahk.get_clipboard(), "Hello world!")
