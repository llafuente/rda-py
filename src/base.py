import time
import logging
import inspect

_undefined = object()
class Base:
    @staticmethod
    def delay(delay):
        """
        Method to introduce a delay

        :param delay (int): Delay in milliseconds
        """
        time.sleep(delay / 1000)

    def debug(self, locals_obj: dict, output = _undefined):

        frame = inspect.currentframe()
        if (frame != None): # typeschecker
            back = frame.f_back
            if (back != None):
                cls = locals_obj["self"].__class__.__name__
                del locals_obj["self"]
                logging.debug(f"{cls}.{back.f_code.co_name} {locals_obj}{'<-- ' + str(output) if output != _undefined else ''}")
                return

        # default in case of failure
        logging.debug(f"? {locals_obj}")

    def _debug(self, text: str):
        frame = inspect.currentframe()
        if (frame != None): # typeschecker
            back = frame.f_back
            if (back != None):
                logging.debug(f"{back.f_code.co_name} {text}")
                return
        # default in case of failure
        logging.debug(f"? {text}")