import re
import time
import pytest
import pytest_mock
import unittest
import logging
from src.window import Window
from src.windows import Windows
from src.keyboard import Keyboard
from src.automation import Automation
import asyncio
from .timer import Timer
from .utils import start

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

def test_keyboard_sendkeys(mocker: pytest_mock.MockerFixture, request, automation, windows, keyboard):
    win = start(automation, request, 'notepad.exe')
    automation.ahk.set_clipboard('')

    automation.ahk.set_clipboard('')
    automation.set_input_mode('interactive')
    win.activate()
    keyboard.send_keys('{CTRL down}a{CTRL up}')
    keyboard.type('xxx{CTRL}')
    keyboard.send_keys('{CTRL down}a{CTRL up}{CTRL down}c{CTRL up}')

    data = automation.ahk.get_clipboard()
    t.assertEqual(data, 'xxx{CTRL}')


    automation.ahk.set_clipboard('')
    automation.set_input_mode('background')
    win.activate()

    with t.assertRaises(ValueError) as cm:
        keyboard.send_keys('?')
    t.assertEqual(str(cm.exception), "hwnd is required when input mode is background")

    with t.assertRaises(ValueError) as cm:
        keyboard.type('?')
    t.assertEqual(str(cm.exception), "hwnd is required when input mode is background")

    keyboard.send_keys('{CTRL down}a{CTRL up}', win.hwnd, 'RichEditD2DPT1')
    keyboard.type('hello world', win.hwnd, 'RichEditD2DPT1')
    keyboard.send_keys('{CTRL down}a{CTRL up}{CTRL down}c{CTRL up}', win.hwnd, 'RichEditD2DPT1')

    data = automation.ahk.get_clipboard()
    t.assertEqual(data, 'hello world')

    # mess characters: ! {
    # example: xxx´ctRL
    # example: hello world1

    t.assertGreater(len(keyboard.get_keyboard_layouts()), 0)

    # [67765257, 67699721]

    t.assertEqual(str(keyboard.get_letter_to_virtualkey('a', 67765257)), '{vk41}')
    t.assertEqual(str(keyboard.get_letter_to_virtualkey('a', 67699721)), '{vk41}')

    t.assertEqual(str(keyboard.get_letter_to_virtualkey('{', 67765257)), '{LControl Down}{LAlt Down}{vkDE}{LControl Up}{LAlt Up}')
    t.assertEqual(str(keyboard.get_letter_to_virtualkey('{', 67699721)), '{LShift Down}{vkDB}{LShift Up}')

    t.assertEqual(str(keyboard.get_letter_to_virtualkey('!', 67765257)), '{LShift Down}{vk31}{LShift Up}')
    t.assertEqual(str(keyboard.get_letter_to_virtualkey('!', 67699721)), '{LShift Down}{vk31}{LShift Up}')

    t.assertEqual(keyboard.get_text_to_sendkeys('hello world!', 67699721), '{vk48}{vk45}{vk4C}{vk4C}{vk4F}{vk20}{vk57}{vk4F}{vk52}{vk4C}{vk44}{LShift Down}{vk31}{LShift Up}')
    # do not press down/up if not necessary
    t.assertEqual(str(keyboard.get_text_to_sendkeys('!!!', 67765257)), '{LShift Down}{vk31}{vk31}{vk31}{LShift Up}')
    t.assertEqual(str(keyboard.get_text_to_sendkeys('{', 67765257)), '{LControl Down}{LAlt Down}{vkDE}{LControl Up}{LAlt Up}')
    t.assertEqual(str(keyboard.get_text_to_sendkeys('~', 67765257)), '{LControl Down}{LAlt Down}{vk34}{LControl Up}{LAlt Up}')

    t.assertEqual(str(keyboard.get_text_to_sendkeys('!!!a', 67765257)), '{LShift Down}{vk31}{vk31}{vk31}{LShift Up}{vk41}')
    t.assertEqual(str(keyboard.get_text_to_sendkeys('{a', 67765257)), '{LControl Down}{LAlt Down}{vkDE}{LControl Up}{LAlt Up}{vk41}')
    t.assertEqual(str(keyboard.get_text_to_sendkeys('~a', 67765257)), '{LControl Down}{LAlt Down}{vk34}{LControl Up}{LAlt Up}{vk41}')

    automation.ahk.set_clipboard('')
    automation.set_input_mode('background')

    keyboard.send_keys(keyboard.get_text_to_sendkeys('hello world!', 67699721), win.hwnd, 'RichEditD2DPT1')

    automation.set_input_mode('interactive')
    keyboard.send_keys('{CTRL down}a{CTRL up}{CTRL down}c{CTRL up}')
    t.assertEqual(automation.ahk.get_clipboard(), 'hello world!')

    win.close()


# test do not expose infomation into logging
# type_password
# send_password