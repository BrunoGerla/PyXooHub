import sys

from typing import Callable, Type

import config
from engine.engine import PyXooEngine
from utils.logger import get_logger, configure_logging
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

    logger.info("Loading Dashboards...")
    registry = get_registry()

    current_dashboard = ask_dashboards(registry)
    engine = PyXooEngine(current_dashboard, frame_interval=config.FRAME_INTERVAL)
    engine.run_forever()

if __name__ == "__main__":
    main()
