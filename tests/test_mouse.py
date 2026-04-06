import re
import time
import pytest
import pytest_mock
import unittest
import logging
from src.rda.windows import Windows
from src.rda.window import Window
from src.rda.automation import Automation
from src.rda.mouse import Mouse
from src.rda.keyboard import Keyboard
import asyncio
from .timer import Timer
from .utils import start, notepad_selectall

# Create a TestCase instance
t = unittest.TestCase()

def test_windows_xxx(caplog: pytest.LogCaptureFixture):

    print(len(caplog.records))


@pytest.fixture
def automation() -> Automation:
    return Automation()


@pytest.fixture
def windows(automation) -> Windows:
    return automation.windows()

@pytest.fixture
def mouse(automation) -> Mouse:
    return automation.mouse()

@pytest.fixture
def keyboard(automation) -> Keyboard:
    return automation.keyboard()



def test_mouse_move(mocker: pytest_mock.MockerFixture, request, automation, windows, mouse):
    mouse.move_to2(0, 0)
    t.assertEqual(mouse.get(), (0,0))
    mouse.move_to2(500, 500)
    t.assertEqual(mouse.get_position(), (500,500))

    mouse.move_rel2(100, 100)
    t.assertEqual(mouse.get(), (600,600))

    #coverage
    automation.set_input_mode('background')
    mouse.move_rel2(100, 100)
    t.assertEqual(mouse.get(), (700,700))
    mouse.move_to2(500, 500)
    t.assertEqual(mouse.get(), (500,500))


def test_mouse_click(mocker: pytest_mock.MockerFixture, request, automation, windows, keyboard, mouse):
    win = start(automation, request, 'notepad.exe')
    win.move(0,0)
    win.resize(1024,768)

    notepad_selectall(win)
    keyboard.send_keys('{BACKSPACE}')
    keyboard.type("hello!")

    mouse.click2(33, 61)

    mouse.right_click2(500, 150)
    #mouse.move_rel2(230, 25)
    mouse.move_rel2(320, 25)
    mouse.sleep(2000)
    mouse.click2()

    keyboard.send_keys("{CTRL down}c{CTRL up}")
    t.assertEqual(automation.ahk.get_clipboard(), "hello!")

    win.close(50, unable_to_close_exception=None)
    win.send_keys("n")


def test_mouse_cursor_notepad(mocker: pytest_mock.MockerFixture, request, automation, windows, keyboard, mouse):
    windows.minimize_all()

    mouse.move_to2(0, 0)
    t.assertEqual(mouse.sleep(1000).get_cursor_id(), 65561)

    win = start(automation, request, 'notepad.exe')
    win.move(0,0)
    win.resize(1024,768)
    sleep = 3000

    win.mouse_move2(400,400)
    t.assertEqual(mouse.sleep(sleep).get_cursor_id(), 65541)
    win.mouse_move2(0,400)
    t.assertEqual(mouse.sleep(sleep).get_cursor_id(), 65553)
    win.mouse_move2(1018,400)
    t.assertEqual(mouse.sleep(sleep).get_cursor_id(), 65553)
    win.mouse_move2(1016, 760)
    t.assertEqual(mouse.sleep(sleep).get_cursor_id(), 65549)
    t.assertEqual(mouse.sleep(sleep).get_cursor(), 'unknown')

def test_mouse_cursor_mspaint(mocker: pytest_mock.MockerFixture, request, automation, windows, keyboard, mouse):
    windows.minimize_all()

    mouse.move_to2(0, 0)
    t.assertEqual(mouse.sleep(1000).get_cursor_id(), 65561)

    win = start(automation, request, 'mspaint.exe')
    win.move(0,0)
    win.resize(1024,768)

    win.mouse_move2(400,400)
    t.assertGreater(mouse.sleep(1000).get_cursor_id(), 0)
    win.mouse_move2(0,400)
    t.assertEqual(mouse.sleep(1000).get_cursor_id(), 65553)
    win.mouse_move2(1024+28,400)
    t.assertEqual(mouse.sleep(1000).get_cursor_id(), 65553)
    win.mouse_move2(1024+24, 768-8)
    t.assertEqual(mouse.sleep(1000).get_cursor_id(), 65549)
    t.assertEqual(mouse.sleep(1000).get_cursor(), 'unknown')