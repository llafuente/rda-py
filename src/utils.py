from functools import wraps
import time

def call_repeat_while_return(func, args, kwargs, ret_value, timeout_ms: int, delay_ms: int, timeout_exception: Exception = TimeoutError("timeout")):
    """
    calls given function until it returns something different from ret_value or timeout is reached.

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
        v = func(*args, **kwargs)

        if (v != ret_value):
            return v

        if (time.time_ns() > max_ms):
            raise timeout_exception

        time.sleep(delay_ms / 1000)

    raise Exception('unreachable code')

def call_repeat_while_not_in(func, args, kwargs, ret_values: list, timeout_ms: int, delay_ms: int, timeout_exception: Exception = TimeoutError("timeout")):
    """
    calls given function until it returns something different from ret_value or timeout is reached.

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
        v = func(*args, **kwargs)

        try:
            ret_values.index(v)
            return v
        except:
            pass

        if (time.time_ns() > max_ms):
            raise timeout_exception

        time.sleep(delay_ms / 1000)

    raise Exception('unreachable code')

def call_repeat_while_exception(func, args, kwargs, timeout_ms: int, delay_ms: int):
    max_ms = time.time_ns() + timeout_ms * 1_000_000
    last_exception = None
    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e

        if (time.time_ns() > max_ms):
            raise last_exception

        time.sleep(delay_ms / 1000)

    raise Exception('unreachable code')

def repeat_while_return(ret_value, timeout_ms: int, delay_ms: int, timeout_exception: Exception = Exception("timeout")):
    """
    decorator that repeat the function until the return type is different from the given one
    """
    def retry_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal ret_value, timeout_ms, delay_ms
            return call_repeat_while_return(func, args, kwargs, ret_value, timeout_ms, delay_ms, timeout_exception)

        return wrapper

    return retry_decorator

def repeat_while_exception(timeout_ms: int, delay_ms: int):
    def retry_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timeout_ms, delay_ms
            return call_repeat_while_exception(func, args, kwargs, timeout_ms, delay_ms)

        return wrapper

    return retry_decorator

def rgba_to_hex_color(r:int, g:int, b:int, a:int) -> str:
    return f'#{r:02x}{g:02x}{b:02x}{a:02x}'

def rgb_to_hex_color(r:int, g:int, b:int) -> str:
    return f'#{r:02x}{g:02x}{b:02x}'

def hex_color_to_rgba(hex_color: str) -> (int, int, int, int):
    # Convert to RGB tuple
    r = int(hex_color[2:4], 16)
    g = int(hex_color[4:6], 16)
    b = int(hex_color[6:8], 16)

    a = 255
    if (len (hex_color) == 10):
        a = int(hex_color[8:10], 16)

    return (r, g, b)