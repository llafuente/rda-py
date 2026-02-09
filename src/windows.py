import pygetwindow as gw
import logging

class Windows:
    def get(self, hidden = False):
        logging.debug(f"(hidden? {hidden})")
        wins = self._get(hidden)
        logging.debug(f"<-- found {len(wins)} windows")

        return wins
  
    def _get(self, hidden) -> list:

        windows = gw.getAllWindows()
        if hidden:
            gw.getAllWindows() # TODO?
        else:
            gw.getAllWindows()

        # windows = gw.getAllTitles()
        logging.debug(windows)

        return windows