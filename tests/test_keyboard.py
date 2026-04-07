import re
import time
import pytest
import pytest_mock
import unittest
import logging
from src.rda.window import Window
from src.rda.windows import Windows
from src.rda.keyboard import Keyboard, VirtualKey
from src.rda.automation import Automation
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
def keyboard(automation) -> Keyboard:
    return automation.keyboard()

def test_keyboard_virtual_keys(mocker: pytest_mock.MockerFixture, request, automation, windows, keyboard):
    keyboards = keyboard.get_keyboard_layouts()
    t.assertGreater(len(keyboards), 0)

    # [67765257, 67699721]
    # 67767306

    if 67765257 in keyboards:
        t.assertEqual(str(keyboard.get_letter_to_virtualkey('a', 67765257)), '{vk41}')
        t.assertEqual(str(keyboard.get_letter_to_virtualkey('{', 67765257)), '{LControl Down}{LAlt Down}{vkDE}{LControl Up}{LAlt Up}')
        t.assertEqual(str(keyboard.get_letter_to_virtualkey('!', 67765257)), '{LShift Down}{vk31}{LShift Up}')
        # do not press down/up if not necessary
        t.assertEqual(str(keyboard.get_text_to_sendkeys('!!!', 67765257)), '{LShift Down}{vk31}{vk31}{vk31}{LShift Up}')
        t.assertEqual(str(keyboard.get_text_to_sendkeys('{', 67765257)), '{LControl Down}{LAlt Down}{vkDE}{LControl Up}{LAlt Up}')
        t.assertEqual(str(keyboard.get_text_to_sendkeys('~', 67765257)), '{LControl Down}{LAlt Down}{vk34}{LControl Up}{LAlt Up}')

        t.assertEqual(str(keyboard.get_text_to_sendkeys('!!!a', 67765257)), '{LShift Down}{vk31}{vk31}{vk31}{LShift Up}{vk41}')
        t.assertEqual(str(keyboard.get_text_to_sendkeys('{a', 67765257)), '{LControl Down}{LAlt Down}{vkDE}{LControl Up}{LAlt Up}{vk41}')
        t.assertEqual(str(keyboard.get_text_to_sendkeys('~a', 67765257)), '{LControl Down}{LAlt Down}{vk34}{LControl Up}{LAlt Up}{vk41}')
    elif 67699721 in keyboards:
        t.assertEqual(str(keyboard.get_letter_to_virtualkey('a', 67699721)), '{vk41}')
        t.assertEqual(str(keyboard.get_letter_to_virtualkey('{', 67699721)), '{LShift Down}{vkDB}{LShift Up}')
        t.assertEqual(str(keyboard.get_letter_to_virtualkey('!', 67699721)), '{LShift Down}{vk31}{LShift Up}')
        t.assertEqual(keyboard.get_text_to_sendkeys('hello world!', 67699721), '{vk48}{vk45}{vk4C}{vk4C}{vk4F}{vk20}{vk57}{vk4F}{vk52}{vk4C}{vk44}{LShift Down}{vk31}{LShift Up}')

def test_keyboard_sendkeys(mocker: pytest_mock.MockerFixture, request, automation, windows, keyboard):
    win = start(automation, request, 'notepad.exe')
    automation.set_action_delay(3000)

    automation.ahk.set_clipboard('')
    automation.set_input_mode('interactive')
    win.activate()
    notepad_selectall(win)
    keyboard.type('xxx{CTRL}')
    notepad_selectall(win)
    keyboard.send_keys('{CTRL down}c{CTRL up}')

    data = automation.ahk.get_clipboard()
    t.assertEqual(data, 'xxx{CTRL}')


    automation.ahk.set_clipboard('')
    win.minimize()
    automation.set_input_mode('background')

    with t.assertRaises(ValueError) as cm:
        keyboard.send_keys('?')
    t.assertEqual(str(cm.exception), "hwnd is required when input mode is background")

    with t.assertRaises(ValueError) as cm:
        keyboard.type('?')
    t.assertEqual(str(cm.exception), "hwnd is required when input mode is background")

    notepad_selectall(win)
    keyboard.type('hello world', win.hwnd, 'RichEditD2DPT1')

    # NOTE! notepad.exe CTRL+a works
    # NOTE! notepad.exe refuse to copy to clipboard while minimized!!!
    win.maximize()
    notepad_selectall(win)
    keyboard.send_keys('{CTRL down}c{CTRL up}', win.hwnd, 'RichEditD2DPT1')
    win.minimize()

    # automation.ahk.msg_box("?")
    data = automation.ahk.get_clipboard()
    t.assertEqual(data, 'hello world')

    # mess characters: ! {
    # example: xxx´ctRL
    # example: hello world1

    automation.ahk.set_clipboard('')
    automation.set_input_mode('background')

    keyboard.send_keys(keyboard.get_text_to_sendkeys('hello world!', 67699721), win.hwnd, 'RichEditD2DPT1')

    win.restore()
    automation.set_input_mode('interactive')
    notepad_selectall(win)
    keyboard.send_keys('{CTRL down}c{CTRL up}')
    t.assertEqual(automation.ahk.get_clipboard(), 'hello world!')

    win.close(50, unable_to_close_exception=None)
    win.send_keys("n")

def test_virtualKey(mocker: pytest_mock.MockerFixture, request, automation, windows, keyboard):
    vkey = VirtualKey('{0x41}', True, True, True)
    t.assertEqual(str(vkey), '{LShift Down}{LControl Down}{LAlt Down}{0x41}{LShift Up}{LControl Up}{LAlt Up}')

def test_get_text_to_sendkeys(mocker: pytest_mock.MockerFixture, request, automation, windows, keyboard):
    #mock get_text_to_virtualkeys
    mocker.patch.object(keyboard, 'get_text_to_virtualkeys', return_value=[VirtualKey('{0x41}', True, True, True)])
    vkeys = keyboard.get_text_to_sendkeys('mock', 67699721)
    t.assertEqual(str(vkeys), '{LShift Down}{LControl Down}{LAlt Down}{0x41}{LShift Up}{LControl Up}{LAlt Up}')


def test_get_text_to_sendkeys2(mocker: pytest_mock.MockerFixture, request, automation, windows, keyboard):
    #mock get_text_to_virtualkeys
    mocker.patch.object(keyboard, 'get_text_to_virtualkeys', return_value=[VirtualKey('{0x41}', True, True, True), VirtualKey('{0x41}', False, False, False), VirtualKey('{0x41}', True, True, True)])
    vkeys = keyboard.get_text_to_sendkeys('mock', 67699721)
    t.assertEqual(str(vkeys), '{LShift Down}{LControl Down}{LAlt Down}{0x41}{LShift Up}{LControl Up}{LAlt Up}{0x41}{LShift Down}{LControl Down}{LAlt Down}{0x41}{LShift Up}{LControl Up}{LAlt Up}')

# test do not expose infomation into logging
# type_password
# send_password

