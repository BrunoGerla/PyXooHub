import time

import config
from engine.pixoo_driver import PixooDriver
from engine.font import Font
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
    BATTERY_INTERVAL = 30.0 # time between updates on the battery

    battery_timer = BATTERY_INTERVAL

    # SETUP PROVIDERS
    mouse = RazerSynapseProvider()

    # SETUP WIDGETS
    title = TextWidget("PYXOOHUB:", x=2, y=3, font=resources.medium_01, color= (255, 255, 255))
    clock = DateTimeWidget(x=2, y=12, font=resources.medium_01, color=(0, 255, 0), format="%H:%M:%S")
    date = DateTimeWidget(x=2, y=20, font=resources.small_font, color=(200, 200, 200), format="%d-%m-%Y", update_interval=60.0)

    mouse_bar = BarWidget(44, 54, width=3, height=7, percentage=0.7
                          , outline_color=(200, 200, 200),
                          color_map=BATTERY_THEME)
    
    mouse_text = TextWidget("00%", 49, 55, font=resources.small_font, color=(200, 200, 200))

    widgets = [title, clock, date, mouse_bar, mouse_text]

    logger.info("Engine Loop Started. Press Ctrl+C to stop.")

    last_time = time.time()

    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Update Widgets
            battery_timer += dt
            if battery_timer >= BATTERY_INTERVAL:
                level = mouse.get_battery_percentage()
                mouse_bar.set_percentage(level)
                mouse_text.text = f"{int(level * 100)}%"
                battery_timer = 0

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