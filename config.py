import logging
from pathlib import Path
import os
from dotenv import load_dotenv
from typing import Any

load_dotenv()

# PROJECT SETTINGS
# Path(__file__) is this file. .parent gives you the folder it's in. We resolve to get the absolute path
PROJECT_ROOT = Path(__file__).parent.resolve()

ASSETS_PATH = PROJECT_ROOT / "assets" / "fonts"


# Pixoo IP and Port
def _get_env(key: str, default: str | None = None) -> str:
    """
    Attempts to get a value from env. If the variable is not set we raise Exception.
    """
    
    value = os.getenv(key)

    if value is None:
        if default is None:
            raise ValueError(f"CRITICAL: Missing required environment variable '{key}' in .env file.")
        return default
    return value

PIXOO_IP = _get_env("PIXOO_IP")
PIXOO_PORT = int(_get_env("PIXOO_PORT", "80")) # default to 80

PIXOO_RETRIES: int = 3 # number of retries on connection
PIXOO_TIMEOUT: int = 10 # number of seconds before timeout

# Log settings
LOG_FILE_NAME = "pyxoo.log"
LOG_FILE_PATH = PROJECT_ROOT / "logs" / LOG_FILE_NAME

FILE_LEVEL = logging.DEBUG
CONSOLE_LEVEL = logging.DEBUG

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