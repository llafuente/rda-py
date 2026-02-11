import logging
import inspect

class Base:
    def _debug(self, text: str):
        frame = inspect.currentframe()
        if (frame != None): # typeschecker
            back = frame.f_back
            if (back != None):
                logging.debug(f"{back.f_code.co_name} {text}")
                return
        # default in case of failure
        logging.debug(f"? {text}")