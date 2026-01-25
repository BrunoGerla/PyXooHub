import logging
from pathlib import Path

# PROJECT SETTINGS
# Path(__file__) is this file. .parent gives you the folder it's in. We resolve to get the absolute path
PROJECT_ROOT = Path(__file__).parent.resolve()


# Log settings
LOG_FILE_NAME = "pyxoo.log"
LOG_FILE_PATH = PROJECT_ROOT / "logs" / LOG_FILE_NAME

FILE_LEVEL = logging.DEBUG
CONSOLE_LEVEL = logging.INFO

DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEBUG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_COLORS = {
    logging.DEBUG: "\x1b[34;20m",       # Grey
    logging.INFO: "\033[0m",            # Default
    logging.WARNING: "\x1b[33;20m",     # Yellow
    logging.ERROR: "\x1b[31;20m",       # Red
    logging.CRITICAL: "\x1b[31;107;1m"  # Red with white background
}