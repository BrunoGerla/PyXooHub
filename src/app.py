import time

import config
from engine.pixoo_driver import PixooDriver
from engine.font import Font
from widgets.datetime import DateTimeWidget
from widgets.text import TextWidget
from widgets.bar import BarWidget
from engine.widget import Widget

from providers.mouse_battery.razer_synapse import RazerSynapseProvider
import resources

from utils.logger import get_logger, configure_logging

configure_logging()
logger = get_logger("MainApp")

def main():
    logger.info("Starting PyXooHub Engine...")

    # initiate the driver
    driver = PixooDriver()

    # Define Colors
    RED = (255, 0, 0)
    AMBER = (255, 160, 0)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)

    BATTERY_THEME = {
        0.15: RED,
        0.30: AMBER,
        0.90: GREEN,
        1.00: CYAN
    }

    # SETUP INTERVALS
    FRAME_INTERVAL = 0.5 # time between frames

    # SETUP PROVIDERS
    mouse = RazerSynapseProvider()

    def get_mouse_text():
        """Formats floats like 0.75 to strings like 75%"""
        val = mouse.get_battery_percentage()
        return f"{int(val*100)}%"

    # SETUP WIDGETS
    title = TextWidget(text="PYXOOHUB:", x=2, y=3, font=resources.medium_01, color= (255, 255, 255))

    clock = DateTimeWidget(x=2, y=12, font=resources.medium_01, color=(0, 255, 0), format="%H:%M:%S")
    date = DateTimeWidget(x=2, y=20, color=(200, 200, 200), format="%d-%m-%Y", update_interval=60.0)

    mouse_bar = BarWidget(x=44,
                          y=54,
                          width=3,
                          height=7,
                          outline_color=(200, 200, 200),
                          color_map=BATTERY_THEME,
                          data_source=mouse.get_battery_percentage,
                          update_interval=30.0)
    
    mouse_text = TextWidget(x=49,
                            y=55,
                            color=(200, 200, 200),
                            data_source=get_mouse_text,
                            update_interval=30.0)

    widgets: list[Widget] = [title, clock, date, mouse_bar, mouse_text]

    logger.info("Engine Loop Started. Press Ctrl+C to stop.")

    last_time = time.time()

    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            for widget in widgets:
                logger.debug(dt)
                widget.update(dt)

            driver.clear()
            for widget in widgets:
                widget.draw(driver)

            # Push to Pixoo
            driver.push()

            now = time.time()
            sleep_time = FRAME_INTERVAL - (now % FRAME_INTERVAL)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger.info("Stopping...")

if __name__ == "__main__":
    main()