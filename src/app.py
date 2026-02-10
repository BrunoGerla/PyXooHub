import time

import config
from engine.pixoo_driver import PixooDriver
from engine.font import Font
from engine.widget import Widget
from engine.color import Color, Colors
from widgets.datetime import DateTimeWidget
from widgets.text import TextWidget
from widgets.bar import BarWidget

from providers.mouse_battery.razer_synapse import RazerSynapseProvider
import resources

from utils.logger import get_logger, configure_logging

configure_logging()
logger = get_logger("MainApp")

def main():
    logger.info("Starting PyXooHub Engine...")

    # initiate the driver
    driver = PixooDriver()

    BATTERY_THEME = {
        0.15: Colors.RED,
        0.30: Colors.AMBER,
        0.90: Colors.GREEN,
        1.00: Colors.CYAN
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
    title = TextWidget(text="I LOVE FLEUR", x=2, y=3, font=resources.medium_01, color=Colors.WHITE)

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
    
    rainbow_square = BarWidget(x=25, y=30,
                               width=10, height=10,
                               color=Colors.RED,
                               percentage=1,
                               outline=False)

    widgets: list[Widget] = [title, clock, date, mouse_bar, mouse_text, rainbow_square]

    logger.info("Engine Loop Started. Press Ctrl+C to stop.")

    last_time = time.time()

    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            if dt > (FRAME_INTERVAL + 0.1): 
                logger.warning(f"LAG SPIKE: Loop took {dt:.3f}s (Target: {FRAME_INTERVAL}s)")

            rainbow_square.current_color = rainbow_square.current_color.shift_hue(dt * 0.1)

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