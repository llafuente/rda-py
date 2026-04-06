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
import threading
from .timer import Timer
from .utils import notepad_save, start, notepad_selectall

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


def notepad_close_without_save(win: Window):
    win.close(0, unable_to_close_exception=None)
    # don't save, win11 mode
    win.sleep(1000)
    win.send_keys("n")

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

    win.move2(0, 0)
    t.assertEqual(win.get_position(), (0,0))

    win.move2(50, 50)
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

        win.move2(50*i,50*i)
        win.mouse_move2(100, 100)
        t.assertEqual(mouse.get(), (50*i+100,50*i+100))
    win.right_click2(200,200)


def test_window_keyboard(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows, mouse: Mouse):
    win = start(automation, request, "notepad.exe")
    win.resize(800, 600)
    win.move2(0,0)
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

    notepad_close_without_save(win)


def test_window_images(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows, mouse: Mouse):
    import os
    cwd = os.path.dirname(os.path.realpath(__file__))

    win = start(automation, request, "mspaint.exe", f'{cwd}\\images\\640x480-green.bmp')
    win.resize(800, 600)
    win.move2(0,0)

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

    win.move2(50, 50)
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


async def mouse_move_in(win: Window, sleep_ms: int, x:int, y: int) -> None:
    logging.debug(f"mouse_move_in {win}")
    await asyncio.sleep(5)
    win.mouse_move2(x, y)
    logging.debug(f"mouse_move_in {win}")


def test_window_image_search(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows, mouse: Mouse):
    import os
    cwd = os.path.dirname(os.path.realpath(__file__))

    MSPAINT_SAVE_POSITION = (206, 37)
    automation.set_action_delay(1000) # increase delay to be sure that "title" dissapear
    win = start(automation, request, "mspaint.exe", f'{cwd}\\images\\640x480-green.bmp')
    win.resize(1024, 768)
    win.move2(0,0)
    win.mouse_move2(0, 0)
    win.send_keys("{CTRL down}0{CTRL up}")

    # window on screen ok
    t.assertEqual(win.has_image(f'{cwd}\\images\\mspaint-save.png', variation=4), True)

    # window minimized ok -> activate
    win.minimize()
    t.assertEqual(win.get_image(f'{cwd}\\images\\mspaint-save.png', variation=4), MSPAINT_SAVE_POSITION)

    # move mouse to occlude the icon
    win.mouse_move2(MSPAINT_SAVE_POSITION[0], MSPAINT_SAVE_POSITION[1])
    with t.assertRaises(Exception) as cm:
        win.get_image(f'{cwd}\\images\\mspaint-save.png', variation=4)
    t.assertEqual(str(cm.exception), "Image not found")


    # wait an image that starts not found -> move mouse and then it's found
    # check that at least pass 2500 ms

    def _move_mouse_after_2500ms():
        time.sleep(2.5)
        win.mouse_move2(0, 0)

    worker = threading.Thread(target=_move_mouse_after_2500ms, daemon=True)
    worker.start()

    started = time.perf_counter()
    t.assertEqual(win.wait_image_appear(f'{cwd}\\images\\mspaint-save.png', variation=4), MSPAINT_SAVE_POSITION)
    elapsed_ms = (time.perf_counter() - started) * 1000
    t.assertGreaterEqual(elapsed_ms, 2500)

    worker.join(timeout=1)


    # wait an image that starts not found -> move mouse and then it's found
    # check that at least pass 2500 ms

    def _move_mouse_after_2500ms():
        time.sleep(2.5)
        win.mouse_move2(MSPAINT_SAVE_POSITION[0], MSPAINT_SAVE_POSITION[1])

    worker = threading.Thread(target=_move_mouse_after_2500ms, daemon=True)
    worker.start()

    started = time.perf_counter()
    t.assertEqual(win.wait_image_disappear(f'{cwd}\\images\\mspaint-save.png', variation=4), True)
    elapsed_ms = (time.perf_counter() - started) * 1000
    t.assertGreaterEqual(elapsed_ms, 2500)

    worker.join(timeout=1)

    # bot example
    if win.wait_image_disappear(f'{cwd}\\images\\mspaint-save.png', variation=4, not_dissapear_exception=None):
        # image dissapear
        t.assertTrue(True)
    else:
        # image still present
        t.assertTrue(False)


    # exceptions paths
    with t.assertRaises(Exception) as cm:
        win.wait_image_appear(f'{cwd}\\images\\640x480-red.bmp', variation=4, timeout=automation.DELAY)
    t.assertEqual(str(cm.exception), "Image not found")
    win.mouse_move2(0, 0)
    with t.assertRaises(Exception) as cm:
        win.wait_image_disappear(f'{cwd}\\images\\mspaint-save.png', variation=4, timeout=automation.DELAY)
    t.assertEqual(str(cm.exception), "Image still present")

    # no expections paths
    t.assertEqual(win.wait_image_disappear(f'{cwd}\\images\\mspaint-save.png', variation=4, timeout=automation.DELAY, not_dissapear_exception=None), False)



def test_window_regions(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows):
    win = start(automation, request, "notepad.exe")
    win.set_position(0, 0)
    win.set_size(800, 600)
    t.assertEqual(win.get_region(), (0, 0, 800, 600))
    t.assertEqual(win.get_rectangle(), (0, 0, 800, 600))

    win.set_position(50, 50)
    t.assertEqual(win.get_region(), (50, 50, 800, 600))
    t.assertEqual(win.get_rectangle(), (50, 50, 850, 650))


def test_window_wait_child(mocker: pytest_mock.MockerFixture, request, automation: Automation, windows: Windows):
    win = start(automation, request, "notepad.exe")
    win.set_position(0, 0)
    win.set_size(800, 600)
    win.send_keys("xxx")

    with t.assertRaises(Exception) as cm:
        dialog = win.wait_child({'classNN': '#32770'}, timeout= 1000, delay=500)
    t.assertEqual(str(cm.exception), "Child window not found")

    # TODO check multiple window found
    logging.debug("------------------------------")
    notepad_save(win)
    dialog = win.wait_child({'classNN': '#32770'}, timeout= 2000, delay=500)
    # child window need some time to process keys
    dialog.sleep(1000).send_keys("{ESC}")

    notepad_close_without_save(win)
