import time

import config
from engine.pixoo_driver import PixooDriver
from engine.font import Font
from widgets.clock import ClockWidget
from widgets.text import TextWidget
from widgets.date import DateWidget
from widgets.bar import BarWidget
import resources

from utils.logger import get_logger, configure_logging

configure_logging()
logger = get_logger("MainApp")

def main():
    logger.info("Starting PyXooHub Engine...")

    # initiate the driver
    driver = PixooDriver()

    # SETUP WIDGETS
    label = TextWidget("PYXOOHUB:", x=2, y=3, font=resources.small_font, color= (200, 200, 200))
    clock = ClockWidget(x=2, y=10, font=resources.medium_01, color=(0, 255, 0))
    date = DateWidget(x=2, y=19, font=resources.small_font, color=(200, 200, 200))
    test = TextWidget("abcdefghijkl", x=2, y=26, font=resources.medium_01, color=(200, 50, 50), space_size=2)
    
    # Mouse %
    mouse_text = TextWidget("MOUSE:", x=32, y=54, font=resources.small_font, color=(200, 200, 200))
    mouse_bar = BarWidget(56, 54, width=3, height=7, percentage=0.7, outline_color=(200, 200, 200))

    logger.info("Engine Loop Started. Press Ctrl+C to stop.")

    try:
        p = 0.0
        while True:
            start_time = time.time()

            # --- RENDER FRAME ----
            driver.clear()
            label.draw(driver)
            clock.draw(driver)
            date.draw(driver)
            test.draw(driver)
            
            # mouse_text.draw(driver)
            mouse_bar.set_percentage(p)

            if p < 0.15:
                mouse_bar.color = (255, 0, 0)
            elif p < 0.30:
                mouse_bar.color = (255, 160, 0)
            elif p > 0.9:
                mouse_bar.color = (0, 255, 255)
            else:
                mouse_bar.color = (0, 255, 0)

            mouse_bar.draw(driver)
            driver.push()
            # ----

            elapsed = time.time() - start_time
            sleep_duration = max(0, 1.0 - elapsed)

            p += 0.1

            if p > 1:
                p = 0.0

            time.sleep(sleep_duration)

    except KeyboardInterrupt:
        logger.info("Stopping...")

if __name__ == "__main__":
    main()