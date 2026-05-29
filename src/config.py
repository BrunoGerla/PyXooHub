import logging
from pathlib import Path
import os
from dotenv import load_dotenv
from typing import Literal, cast

load_dotenv()

# PROJECT SETTINGS
# Path(__file__) is this file. .parent gives you the folder it's in. We resolve to get the absolute path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

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

def _get_bool_env(key: str, default: bool) -> bool:
    value = os.getenv(key)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}

def _get_int_env(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"CRITICAL: Environment variable '{key}' must be an integer.") from exc

ResetPolicy = Literal["always", "periodic", "first", "never"]

def _get_reset_policy() -> ResetPolicy:
    value = _get_env("PIXOO_RESET_POLICY", "always").strip().lower()
    valid_policies: set[ResetPolicy] = {"always", "periodic", "first", "never"}

    if value not in valid_policies:
        raise ValueError(
            "CRITICAL: PIXOO_RESET_POLICY must be one of: "
            f"{', '.join(sorted(valid_policies))}."
        )

    return cast(ResetPolicy, value)

PIXOO_IP = _get_env("PIXOO_IP")
PIXOO_PORT = int(_get_env("PIXOO_PORT", "80")) # default to 80

PIXOO_RETRIES: int = 3 # number of retries on connection
PIXOO_TIMEOUT: int = 5 # number of seconds before timeout
FRAME_INTERVAL: float = 0.5
PIXOO_ASYNC_PUSH: bool = _get_bool_env("PIXOO_ASYNC_PUSH", True)
PIXOO_SKIP_UNCHANGED_FRAMES: bool = _get_bool_env("PIXOO_SKIP_UNCHANGED_FRAMES", True)
PIXOO_LOG_FRAME_STATUS_INTERVAL: int = _get_int_env("PIXOO_LOG_FRAME_STATUS_INTERVAL", 60)

# Resetting the HTTP GIF id clears the Pixoo's uploaded animation slot. The Pixoo is most reliable
# when this happens before each replacement frame; experimental policies can reduce HTTP chatter.
PIXOO_RESET_POLICY: ResetPolicy = _get_reset_policy()
PIXOO_RESET_EVERY_FRAMES: int = _get_int_env("PIXOO_RESET_EVERY_FRAMES", 120)

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
