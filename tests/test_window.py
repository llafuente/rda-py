import re
import time
import pytest
import pytest_mock
import unittest
import logging
from src.rda.window import Window
from src.rda.windows import Windows
from src.rda.windowsearch import WindowSearch
from src.rda.automation import Automation
from src.rda.mouse import Mouse
import asyncio
from .timer import Timer
from .utils import start, notepad_selectall

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
    t.assertIsNotNone(win.title)
    t.assertIsNotNone(win.process)
    t.assertIsNotNone(win.pid)
    t.assertIsNotNone(win.path)
    t.assertIsNotNone(win.classNN)
    t.assertEqual(win.alive, win.is_alive())
    t.assertEqual(win.is_alive(), not win.is_dead())
    t.assertEqual(win.is_alive(), not win.is_closed())
    t.assertEqual(win.is_foreground(), win.is_activated())
    t.assertEqual(win.is_background(), win.is_deactivated())

    win.set_title("xxx")
    t.assertEqual(win.title, "xxx")

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
    notepad_selectall(win)
    win.send_keys("{BACKSPACE}")
    win.type("Hello world!")
    win.type_password("Hello world!")
    win.send_keys("xxx")
    win.send_password("yyy")
    notepad_selectall(win)
    win.send_keys("{CTRL down}c{CTRL up}")
    t.assertEqual(automation.ahk.get_clipboard(), "Hello world!Hello world!xxxyyy")

    with t.assertRaises(Exception) as cm:
        win.close(50)
    t.assertEqual(str(cm.exception), "Could not close window")

    win.close(0, unable_to_close_exception=None)
    # don't save, win11 mode
    win.sleep(1000)
    win.send_keys("n")


def test_window_images(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows, mouse: Mouse):
    import os
    cwd = os.path.dirname(os.path.realpath(__file__))

    win = start(automation, request, "mspaint.exe", f'{cwd}\\images\\640x480-green.bmp')
    win.resize(800, 600)
    win.move(0,0)

    win.mouse_move2(400,400)
    #   rr  gg  bb
    #0x 22  B1  4C
    #   34 177  76
    color = win.get_pixel_color(500, 500)
    t.assertEqual(color, (0,255,0))

    # out of screen pixel
    color = win.get_pixel_color(9999, 1)
    t.assertEqual(color, (255,255,255))

    win.click2(500, 500)
    win.mouse_move2(0, 0)
    color = win.get_pixel_color(500, 500)

    pos = win.find_pixel_color(495, 495, 10, 10, color)
    # paints the next pixel
    t.assertEqual(pos, (501, 499))

    win.move(50, 50)
    pos = win.find_pixel_color(495, 495, 10, 10, color)
    # paints the next pixel
    t.assertEqual(pos, (501, 499))

    #not found
    with t.assertRaises(Exception) as cm:
        pos = win.find_pixel_color(495, 495, 10, 10, (255, 255, 255))
    t.assertEqual(str(cm.exception), "pixel color not found")

    t.assertIsNone(win.find_pixel_color(495, 495, 10, 10, (255, 255, 255), not_found_exception=None))

    # coverage
    win.double_click2(475, 475)
    win.mouse_move2(0,0)
    t.assertEqual(win.get_pixel_color(475, 475), color)

    win.close(250, unable_to_close_exception=None)


    win.get_child({'classNN': 'XAMLModalWindow'}).send_keys("n")
    win.sleep(250)

def test_window_get_child_errors(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows):
    win = start(automation, request, "notepad.exe")
    win.activate()

    with t.assertRaises(Exception) as cm:
        win.get_child({'classNN': 'NotExist'})
    t.assertEqual(str(cm.exception), "Window not found")


def test_window_state(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows):
    win = start(automation, request, "notepad.exe")
    win.activate()

    t.assertTrue(win.restored)
    win.maximize()
    t.assertTrue(win.maximized)
    t.assertFalse(win.minimized)
    win.minimize()
    t.assertTrue(win.minimized)
    win.maximize()
    win.restore()
    t.assertTrue(win.restored)