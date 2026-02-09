import unittest
import logging
from src.automation import Automation



class TestAutomation(unittest.TestCase):
    def setUp(self):
        self.automation = Automation()

    def test_set_key_delay(self):
        self.automation.set_key_delay(100)
        self.assertEqual(self.automation.key_delay, 100)

    def test_set_mouse_delay(self):
        self.automation.set_mouse_delay(200)
        self.assertEqual(self.automation.mouse_delay, 200)

    def test_set_send_mode(self):
        self.automation.set_send_mode("Input")
        self.assertEqual(self.automation.send_mode, "Input")

    # test set_send_mode exception
    def test_set_send_mode_exception(self):
        with self.assertRaises(ValueError) as cm:
            self.automation.set_send_mode("xxx")
        self.assertEqual(str(cm.exception), "'xxx' is not in list")


if __name__ == '__main__':
    unittest.main()