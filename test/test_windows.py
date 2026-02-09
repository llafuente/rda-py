import pytest
import unittest
import logging
from src.windows import Windows

def test_xxx(caplog: pytest.LogCaptureFixture):

    print(len(caplog.records))


class TestWindows(unittest.TestCase):
    def setUp(self):
        self.windows = Windows()

    def test_get_all_windows(self):

        # Assuming there are at least one window on the system
        all_windows = self.windows.get(hidden=True)
        self.assertGreater(len(all_windows), 0)

    def test_get_visible_windows(self):
        # Assuming there are at least one visible window on the system
        visible_windows = self.windows.get(hidden=False)
        self.assertGreater(len(visible_windows), 0)
        # all windows shall have hwnd
        for window in visible_windows:
            print(window)
            self.assertTrue(window.size)
            # can be empty
            self.assertIsNotNone(window.title)


if __name__ == '__main__':
    unittest.main()