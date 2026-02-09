import pygetwindow as gw
import logging

class Windows:
    def get(self, hidden = False):
        """
        Retrieves all windows
        
        Args:
           hidden (bool): If True, include hidden windows. Defaults to False.

        Example:
        >>> import Automation from rda
        >>> Automation().windows().get(hidden=True)
        """
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