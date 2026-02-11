import time
import logging
import inspect

class Base:
    @staticmethod
    def delay(delay):
        """
        Method to introduce a delay

        :param delay (int): Delay in milliseconds
        """
        time.sleep(delay / 1000)

    def _debug(self, text: str):
        frame = inspect.currentframe()
        if (frame != None): # typeschecker
            back = frame.f_back
            if (back != None):
                logging.debug(f"{back.f_code.co_name} {text}")
                return
        # default in case of failure
        logging.debug(f"? {text}")