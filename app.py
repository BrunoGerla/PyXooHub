import time

import config
from engine.pixoo_driver import PixooDriver
from engine.font import Font
from widgets.clock import ClockWidget
from widgets.text import TextWidget
from resources import small_font

from utils.logger import get_logger, configure_logging

configure_logging()
logger = get_logger("MainApp")

def main():
    logger.info("Starting PyXooHub Engine...")

    # initiate the driver
    driver = PixooDriver()

    # SETUP WIDGETS
    label = TextWidget("TIME:", x=2, y=3, font=small_font, color= (200, 200, 200))

    clock = ClockWidget(x=2, y=10, font=small_font, color=(0, 255, 0))

    logger.info("Engine Loop Started. Press Ctrl+C to stop.")

    try:
        while True:
            start_time = time.time()

            # --- RENDER FRAME ----
            driver.clear()
            label.draw(driver)
            clock.draw(driver)
            driver.push()
            # ----

            elapsed = time.time() - start_time
            sleep_duration = max(0, 1.0 - elapsed)
            time.sleep(sleep_duration)

    except KeyboardInterrupt:
        logger.info("Stopping...")

if __name__ == "__main__":
    main()