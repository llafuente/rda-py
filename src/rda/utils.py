from functools import wraps
import time

from typing import Any, Callable, TypeVar, Tuple, Union

T = TypeVar("T")


def loop_until(func: Callable[..., Tuple[bool, T]], timeout_ms: int, delay_ms: int, timeout_exception: Union[Exception, None] = TimeoutError("timeout")) -> T:
    """
    undertanding timing:
    timeout = 150, delay = 100, your_func_time = 0 -> 3 attempts
    0, 100, 200 (timeout)

    timeout = 150, delay = 100, your_func_time = 100 -> 2 attempts
    0, 200 (timeout)

    timeout = 150, delay = 100, your_func_time = 200 -> 1 attempts
    0 (timeout)
    """
    max_ms = time.time_ns() + timeout_ms * 1_000_000

    while True:
        cont, v = func()

        if not cont:
            return v

        if (time.time_ns() > max_ms):
            if timeout_exception is None:
                return v
            raise timeout_exception

        time.sleep(delay_ms / 1000)

    raise RuntimeError("unreachable code") # pragma: no cover

def rgba_to_hex_color(r:int, g:int, b:int, a:int) -> str:
    """
    Converts RGBA values to a hex color string.

    :param r: Red component (0-255)
    :param g: Green component (0-255)
    :param b: Blue component (0-255)
    :param a: Alpha component (0-255)
    :return: Hex color string (e.g., '0xRRGGBBAA')
    """
    return f'0x{r:02x}{g:02x}{b:02x}{a:02x}'

def rgb_to_hex_color(r:int, g:int, b:int) -> str:
    """
    Converts RGB values to a hex color string.

    :param r: Red component (0-255)
    :param g: Green component (0-255)
    :param b: Blue component (0-255)
    :return: Hex color string (e.g., '0xRRGGBB')
    """
    return f'0x{r:02x}{g:02x}{b:02x}'

Color = Union[Tuple[int, int, int, int], Tuple[int, int, int]]

def hex_color_to_rgba(hex_color: str) -> Color:
    """
    Converts a hex color string to an RGBA tuple.

    :param hex_color: Hex color string (e.g., '0xRRGGBB' or '0xRRGGBBAA')
    :return: Tuple of (R, G, B, A)
    """
    # Convert to RGB tuple
    r = int(hex_color[2:4], 16)
    g = int(hex_color[4:6], 16)
    b = int(hex_color[6:8], 16)

    a = 255
    if (len (hex_color) == 10):
        a = int(hex_color[8:10], 16)
        return (r, g, b, a)

    return (r, g, b)