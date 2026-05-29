import sys

from typing import Callable, Type

import config
from engine.engine import PyXooEngine
from utils.logger import get_logger, configure_logging
from engine.dashboard import Dashboard

DashboardBuilder = Callable[[], Dashboard] | Type[Dashboard]

configure_logging()
logger = get_logger("MainApp")


class PyXooApp:
    """
    Loads dashboards, handles CLI selection, and starts the engine.
    """

    def __init__(self, frame_interval: float = config.FRAME_INTERVAL):
        self.frame_interval = frame_interval

    def run(self):
        logger.info("Starting PyXooHub Engine...")
        logger.info("Loading dashboards...")

        registry = self.get_registry()
        dashboard = self.ask_dashboard(registry)
        engine = PyXooEngine(dashboard, frame_interval=self.frame_interval)
        engine.run_forever()

    def get_registry(self) -> dict[str, DashboardBuilder]:
        from default_dashboards import DEFAULT_DASHBOARDS

        registry = dict(DEFAULT_DASHBOARDS)

        try:
            from dashboards import CUSTOM_DASHBOARDS

            registry.update(CUSTOM_DASHBOARDS)
        except ImportError:
            logger.warning("No 'dashboards.py' found. Using defaults only.")

        return registry

    def ask_dashboard(self, registry: dict[str, DashboardBuilder]) -> Dashboard:
        options = list(registry.items())
        if not options:
            raise RuntimeError("No dashboards are registered.")

        for i, (name, _) in enumerate(options):
            print(f"[{i}]: {name}")

        while True:
            try:
                choice = input(f"Enter number (0-{len(options)-1}): ").strip()
                selection_index = int(choice)

                if 0 <= selection_index < len(options):
                    selected_name, dashboard_builder = options[selection_index]
                    logger.info(f"Selected: {selected_name}")
                    return dashboard_builder()

                print("Invalid number. Try again.")
            except ValueError:
                print("Please enter a valid number.")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                sys.exit(0)

def main():
    app = PyXooApp()
    app.run()

if __name__ == "__main__":
    main()
