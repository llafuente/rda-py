from functools import wraps
import time

def call_repeat_while_return(func, args, kwargs, ret_value, timeout_ms: int, delay_ms: int, timeout_exception: Exception = Exception("timeout")):
    max_ms = time.time_ns() + timeout_ms * 1_000_000

    while True:
        v = func(*args, **kwargs)

        if (v != ret_value):
            return v

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