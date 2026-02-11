import time
import unittest

class Timer:
    """Context manager for measuring elapsed time in milliseconds."""
    start = None
    end = None
    #: elapsed time in miliseconds
    elapsed_ms = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self  # Allows access to elapsed_ms after the block

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()
        self.elapsed_ms = (self.end - self.start) * 1000  # Convert to ms