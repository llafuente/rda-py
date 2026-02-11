import time
import pytest
import unittest
import logging
from src.window import Window
from src.windows import Windows
from src.automation import Automation
import asyncio
from .timer import Timer

# Create a TestCase instance
t = unittest.TestCase()

def test_xxx(caplog: pytest.LogCaptureFixture):

    print(len(caplog.records))


@pytest.fixture
def automation() -> Automation:
    return Automation()

@pytest.fixture
def windows(automation) -> Windows:
    return automation.windows()

def test_get_all_windows(windows):

    # Assuming there are at least one window on the system
    all_windows = windows.get(hidden=True)
    t.assertGreater(len(all_windows), 0)

def test_get_visible_windows(windows):
    # Assuming there are at least one visible window on the system
    visible_windows = windows.get(hidden=False)
    t.assertGreater(len(visible_windows), 0)
    # all windows shall have hwnd
    for window in visible_windows:
        print(window)
        #t.assertTrue(window.size)
        # can be empty
        t.assertIsNotNone(window.title)
        t.assertIsNotNone(window.pid)
        t.assertIsNotNone(window.process)
        t.assertIsNotNone(window.path)
        t.assertIsNotNone(window.classNN)
        
def test_not_found(windows):
    with t.assertRaises(Exception) as cm:
        windows.find_one({"process": "xxx.exe"})
    t.assertEqual(str(cm.exception), "Window not found")

    with t.assertRaises(Exception) as cm:
        windows.find_one({"process": "explorer.exe"})
    t.assertEqual(str(cm.exception), "Multiple windows found")

def test_get_foreground(windows):
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
    win.close()

def test_title_change(automation, windows):
    asyncio.run(title_change(automation, windows))