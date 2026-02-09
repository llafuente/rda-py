# pytest configuration file
# conftest.py
import pytest
import logging

logging.basicConfig(
    filename='latest.log',  # Log file name
    filemode='w',        # Mode 'w' to overwrite the log file each time the application starts
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    level=logging.DEBUG  # Set the logging level to DEBUG
)

logger = logging.getLogger(__name__)
logger.debug("TEST START")
