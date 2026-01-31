import logging
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent))

import config


class ColorfulFormatter(logging.Formatter):
    """
    Custom formatter that assigns colours based on logging level.
    """
    def __init__(self, log_colors: dict[int, str] = config.LOG_COLORS, default_format: str = config.DEFAULT_FORMAT, debug_format: str = config.DEBUG_FORMAT, datefmt: str | None = None):
        super().__init__()
        self.datefmt = datefmt
        self.formatters = {}

        for level, color_code in log_colors.items():
            
            if level == logging.DEBUG:
                fmt_string = debug_format
            else:
                fmt_string = default_format
            
            # Combine: Color + Format + Reset
            colored_fmt = f"{color_code}{fmt_string}{"\x1b[0m"}"
            
            self.formatters[level] = logging.Formatter(colored_fmt, datefmt=self.datefmt)

    def format(self, record):
        formatter = self.formatters.get(record.levelno)
        if formatter is None:
            formatter = self.formatters[logging.INFO]
        return formatter.format(record)

def configure_logging(
        logging_path: Path = config.LOG_FILE_PATH,
        file_level: int = config.FILE_LEVEL,
        console_level: int = config.CONSOLE_LEVEL,
        log_format: str = config.DEFAULT_FORMAT,
        date_format: str = config.DATE_FORMAT
        ):
    """
    Sets up the ROOT logger.
    """

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # if the logger already has handlers, return
    if root_logger.hasHandlers():
        return
    
    # if the log folder doesn't exist yet, we make it
    if not logging_path.parent.exists():
        logging_path.parent.mkdir(parents=True, exist_ok=True)

    # add file handler
    file_handler = logging.FileHandler(logging_path, mode="w", encoding="utf-8") # we use mode="w" for now but in production change to a rotating file handler where mode="a"
    file_handler.setLevel(file_level)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColorfulFormatter(datefmt=date_format))

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def get_logger(name: str):
    """
    Returns a logger instance named 'name'
    """
    return logging.getLogger(name)


if __name__ == "__main__":
    configure_logging()

    logger = get_logger("Logger Debug")
    
    print("Standard print.")

    logger.debug("This is some debugging")
    logger.info("This is some info")
    logger.warning("This is a warning")
    logger.error("This is an error!")
    logger.critical("This is a critical error!")