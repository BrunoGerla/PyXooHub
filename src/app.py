import time
import config
from engine.pixoo_driver import PixooDriver
from utils.logger import get_logger, configure_logging

from default_dashboards import build_cyberpunk_dashboard

try:
    from dashboards import build_default_dashboard
    current_dashboard = build_default_dashboard()
except ImportError:
    from default_dashboards import build_cyberpunk_dashboard
    current_dashboard = build_cyberpunk_dashboard()

configure_logging()
logger = get_logger("MainApp")

def main():
    logger.info("Starting PyXooHub Engine...")
    
    # 1. Initialize the Hardware Driver
    driver = PixooDriver()

    # --- CONFIG ---
    # 0.1s is smooth enough for clock seconds to tick accurately
    FRAME_INTERVAL = 0.5

    logger.info(f"Engine Loop Started with {len(current_dashboard.widgets)} widgets.")
    last_time = time.time()
    
    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # --- ENGINE UPDATE ---
            # 1. Update logic (Clocks tick, data fetches)
            current_dashboard.update(dt)
            
            # 2. Draw to buffer
            driver.clear()
            current_dashboard.draw(driver)
            
            # 3. Send to device
            driver.push()

            # --- SLEEP ---
            now = time.time()
            sleep_time = FRAME_INTERVAL - (now % FRAME_INTERVAL)
            time.sleep(max(0, sleep_time)) 

    except KeyboardInterrupt:
        logger.info("Stopping...")

if __name__ == "__main__":
    main()