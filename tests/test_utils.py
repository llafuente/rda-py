import time
import pytest
import unittest
import logging
from src.rda.utils import hex_color_to_rgba, rgb_to_hex_color, rgba_to_hex_color
from src.rda.windows import Windows
from src.rda.automation import Automation

t = unittest.TestCase()

def test_hex_color_to_rgba():
    automation = Automation()
    hex_color = "0xFF5733"
    expected_rgba = (255, 87, 51)
    t.assertEqual(hex_color_to_rgba(hex_color), expected_rgba)

    hex_color = "0xFF5733FF"
    expected_rgba = (255, 87, 51, 255)
    t.assertEqual(hex_color_to_rgba(hex_color), expected_rgba)

    hex_color = "0xFF573300"
    expected_rgba = (255, 87, 51, 0)
    t.assertEqual(hex_color_to_rgba(hex_color), expected_rgba)

def test_rgba_to_hex_color():
    automation = Automation()
    rgba_color = (255, 87, 51, 255)
    expected_hex_color = "0xff5733ff"
    t.assertEqual(rgba_to_hex_color(rgba_color[0], rgba_color[1], rgba_color[2], rgba_color[3]), expected_hex_color)

    rgba_color = (255, 87, 51, 0)
    expected_hex_color = "0xff573300"
    t.assertEqual(rgba_to_hex_color(rgba_color[0], rgba_color[1], rgba_color[2], rgba_color[3]), expected_hex_color)


def test_rgb_to_hex_color():
    automation = Automation()
    rgb_color = (255, 87, 51)
    expected_hex_color = "0xff5733"
    t.assertEqual(rgb_to_hex_color(rgb_color[0], rgb_color[1], rgb_color[2]), expected_hex_color)

if __name__ == '__main__':
    unittest.main()