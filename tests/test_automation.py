import unittest
import logging
from src.automation import Automation



class TestAutomation(unittest.TestCase):
    def setUp(self):
        self.automation = Automation()

    def test_set_key_delay(self):
        self.automation.set_key_delay(101)
        self.assertEqual(self.automation.key_delay, 101)

        self.automation.set_press_duration(101)
        self.assertEqual(self.automation.press_duration, 101)

        self.automation.set_mouse_delay(201)
        self.assertEqual(self.automation.mouse_delay, 201)

        self.automation.set_send_mode("Input")
        self.assertEqual(self.automation.send_mode, "Input")

        self.automation.set_send_mode("Play")
        self.assertEqual(self.automation.send_mode, "Play")

    # test set_send_mode exception
    def test_set_send_mode_exception(self):
        with self.assertRaises(ValueError) as cm:
            self.automation.set_send_mode("xxx")
        self.assertEqual(str(cm.exception), "Invalid send mode: xxx")

    def test_unimplemented(self):
        assert self.automation.UIA == None
        assert self.automation.JAB == None
        # just for coverage purposes...
        self.automation.delay(50)

if __name__ == '__main__':
    unittest.main()