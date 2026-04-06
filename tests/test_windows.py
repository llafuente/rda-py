import re
import time
import pytest
import pytest_mock
import unittest
import logging
from src.rda.window import Window
from src.rda.windows import Windows
from src.rda.automation import Automation
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

def test_windows_get_all_windows(windows):

    # Assuming there are at least one window on the system
    all_windows = windows.get(include_hidden=True)
    t.assertGreater(len(all_windows), 0)

def test_windows_get_visible_windows(windows):
    # Assuming there are at least one visible window on the system
    visible_windows = windows.get(include_hidden=False)
    t.assertGreater(len(visible_windows), 0)
    # all windows shall have hwnd
    for window in visible_windows:
        print(window)
        #t.assertTrue(window.size)
        # can be empty
        t.assertIsNotNone(window.hwnd)
        t.assertIsNotNone(window.title)
        t.assertIsNotNone(window.pid)
        t.assertIsNotNone(window.process)
        t.assertIsNotNone(window.path)
        t.assertIsNotNone(window.classNN)

def test_windows_not_found(windows):
    with t.assertRaises(Exception) as cm:
        windows.find_one({"process": "xxx.exe"})
    t.assertEqual(str(cm.exception), "Window not found")

    with t.assertRaises(Exception) as cm:
        windows.find_one({"process": "explorer.exe"})
    t.assertEqual(str(cm.exception), "Multiple windows found")

    with t.assertRaises(Exception) as cm:
        windows.find_one({"path": "imposible path"})
    t.assertEqual(str(cm.exception), "Window not found")

    wins = windows.find({"path": "C:\\"})
    t.assertGreater(len(wins), 0, "Found multiple applications runnning on C:\\")

    wins = windows.find({"process": "explorer.exe"})
    t.assertGreater(len(wins), 0, "Found multiple explorer windows")

# test regex and hidden process logic
def test_windows_windows_regex(windows):
    with t.assertRaises(Exception) as cm:
        windows.find_one({"process": re.compile("^Explorer.*")}, include_hidden=True)
    t.assertEqual(str(cm.exception), "Multiple windows found")

    with t.assertRaises(Exception) as cm:
        windows.find_one({"title": re.compile("^imposible window title.*")}, include_hidden=True)
    t.assertEqual(str(cm.exception), "Window not found")

    with t.assertRaises(Exception) as cm:
        windows.find_one({"title": "imposible window title"}, include_hidden=True)
    t.assertEqual(str(cm.exception), "Window not found")

def test_windows_get_foreground(windows):
    win = windows.get_foreground()
    t.assertTrue(win.hwnd)


#
# change title tests
#

async def change_title(win: Window, new_title: str) -> None:
    logging.debug(f"change_title start {new_title}")
    await asyncio.sleep(5)
    win.set_title(new_title)
    logging.debug(f"change_title end {new_title}")

async def wait_until_title_change_to(win: Window, new_title: str):
    previous_title = win.title
    with Timer() as timer:
        await win.wait_until_title_change_to(new_title)

    t.assertGreater(timer.elapsed_ms, 2000, "at least elapsed 2s")
    t.assertEqual(win.title, new_title)

async def wait_until_title_change_from(win: Window):
    previous_title = win.title
    with Timer() as timer:
        await win.wait_until_title_change_from()

    t.assertGreater(timer.elapsed_ms, 2000, "at least elapsed 2s")
    t.assertNotEqual(win.title, previous_title)



async def title_change(automation: Automation, windows: Windows):
    # start notepad.exe process
    automation.ahk.run_script('run notepad.exe')
    time.sleep(2.5)
    win = windows.find_one({"process": "notepad.exe"})
    t.assertIsNotNone(win)
    t.assertIsNotNone(win.title)

    win2 = automation.window_from_hwnd(win.hwnd)
    t.assertEqual(win.title, win2.title)

    # change title to!
    await asyncio.gather(
        change_title(win, "xxx"),
        wait_until_title_change_to(win, "xxx")
    )

    await asyncio.gather(
        change_title(win, "xxx2"),
        wait_until_title_change_from(win)
    )

    # test exceptions
    with t.assertRaises(Exception) as cm:
        await win.wait_until_title_change_from(timeout=500)
    t.assertEqual(str(cm.exception), "Timeout after 500ms waiting for title change")

    with t.assertRaises(Exception) as cm:
        await win.wait_until_title_change_to(new_title="imposible title", timeout=500)
    t.assertEqual(str(cm.exception), "Timeout after 500ms waiting for title change")

    win.close()
    t.assertFalse(win.is_alive())

def test_windows_title_change(automation, windows):
    asyncio.run(title_change(automation, windows))

def test_windows_foreground_exception(mocker, automation, windows):
    ahk_get_active_window = mocker.patch.object(automation.ahk, "get_active_window", return_value=None)
    with t.assertRaises(Exception) as cm:
        windows.get_foreground()
    t.assertEqual(str(cm.exception), "Could not get foregound window")
    ahk_get_active_window.assert_called_once_with()

def test_windows_close_exception(mocker: pytest_mock.MockerFixture, request, automation, windows):
    win = start(automation, request, "notepad.exe")

    # ahk_win_close = mocker.patch.dict(automation.ahk, "win_close", return_value=None)
    original_win_close = automation.ahk.win_close
    ahk_win_close = mocker.patch.object(automation.ahk, "win_close", return_value=None)
    with t.assertRaises(Exception) as cm:
        win.close()
    print(cm.exception)
    t.assertEqual(str(cm.exception), "Could not close window")
    ahk_win_close.assert_called_once()
    ahk_win_close.reset_mock()
    # restore original so Notepad could be closed!
    automation.ahk.win_close = original_win_close