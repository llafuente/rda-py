import inspect
import unittest
import pytest
import pytest_mock

from src.automation import Automation

# Create a TestCase instance
t = unittest.TestCase()

@pytest.fixture
def automation() -> Automation:
    return Automation()

def test_set_key_delay(automation: Automation):
    automation.set_key_delay(101)
    t.assertEqual(automation.key_delay, 101)

    automation.set_press_duration(101)
    t.assertEqual(automation.press_duration, 101)

    automation.set_send_mode("Input")
    t.assertEqual(automation.send_mode, "Input")

    automation.set_send_mode("Play")
    t.assertEqual(automation.send_mode, "Play")

# test set_send_mode exception
def test_set_send_mode_exception(automation: Automation):
    with t.assertRaises(ValueError) as cm:
        automation.set_send_mode("xxx")
    t.assertEqual(str(cm.exception), "Invalid send mode: xxx")

def test_unimplemented(automation: Automation):
    assert automation.UIA == None
    assert automation.JAB == None

def test_coverage(automation: Automation, mocker: pytest_mock.MockerFixture):
    # just for coverage purposes...
    automation.delay(50)

    mocker.patch.object(inspect, "currentframe", return_value=None)
    automation._debug("xx")
