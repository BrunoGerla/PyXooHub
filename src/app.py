import sys
import time
import config

from typing import Callable, Type

from engine.pixoo_driver import PixooDriver
from utils.logger import get_logger, configure_logging
from utils.container_tree import print_layout_tree
from engine.dashboard import Dashboard

DashboardBuilder = Callable[[], Dashboard] | Type[Dashboard]

configure_logging()
logger = get_logger("MainApp")

def get_registry() -> dict[str, DashboardBuilder]:
    from default_dashboards import DEFAULT_DASHBOARDS
    registry = DEFAULT_DASHBOARDS

    try:
        from dashboards import CUSTOM_DASHBOARDS
        registry.update(CUSTOM_DASHBOARDS)
    except ImportError:
        logger.warning("No 'custom_dashboards.py' found. Using defaults only.")

    return registry

def ask_dashboards(registry: dict[str, DashboardBuilder]) -> Dashboard:
    options = list(registry.items())
    for i, (name, _) in enumerate(options):
        print(f"[{i}]: {name}")

    while True:
        try:
            choice = input(f"Enter number (0-{len(options)-1}): ").strip()
            selection_index = int(choice)
            
            if 0 <= selection_index < len(options):
                selected_name, dashboard_cls = options[selection_index]
                logger.info(f"Selected: {selected_name}")
                return dashboard_cls()
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Please enter a valid number.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

def main():
    logger.info("Starting PyXooHub Engine...")
    
    driver = PixooDriver()

    logger.info("Loading Dashboards...")
    registry = get_registry()

    current_dashboard = ask_dashboards(registry)

    # --- CONFIG ---
    FRAME_INTERVAL = 0.5

    # logger.info(f"Engine Loop Started with {len(current_dashboard.widgets)} widgets.")
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