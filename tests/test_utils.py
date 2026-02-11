import time
import pytest
import unittest
import logging
from src.windows import Windows
from src.automation import Automation
from src.utils import repeat_while_exception, repeat_while_return, call_repeat_while_return

xxx_count = 0
@repeat_while_return(False, 1000, 100)
def fixture_xxx():
    global xxx_count

    print(f"fixture_xxx{xxx_count}")
    if (xxx_count > 5):
        raise Exception("to many retries!")

    xxx_count+=1
    if (xxx_count == 5):
        return True

    return False

xxx2_count = 0
@repeat_while_return(False, 50, 100)
def fixture_xxx2():
    global xxx2_count
    xxx2_count += 1
    if (xxx2_count == 5):
        return True

    return False


class fix_counter:
    count = 0
    def add_one(self):
        self.count += 1
        if (self.count == 5):
            return True

        return False


class TestWindows(unittest.TestCase):
    def test_repeat_while_return(self):
        assert fixture_xxx() == True

        with self.assertRaises(Exception) as cm:
            fixture_xxx()
        self.assertEqual(str(cm.exception), "to many retries!")

    def test_repeat_while_return2(self):
        with self.assertRaises(Exception) as cm:
            fixture_xxx2()
        self.assertEqual(str(cm.exception), "timeout")
        self.assertEqual(xxx2_count, 2)

    def test_repeat_while_return_class(self):
        counter = fix_counter()
        
        assert call_repeat_while_return(counter.add_one, [], {}, False, 1000, 50) == True
        
        counter.count = 0
        with self.assertRaises(Exception) as cm:
            call_repeat_while_return(counter.add_one, [], {}, False, 50, 100)
        self.assertEqual(str(cm.exception), "timeout")
        self.assertEqual(counter.count, 2)

if __name__ == '__main__':
    unittest.main()