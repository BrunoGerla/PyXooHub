import time

from engine.dashboard import Dashboard
from engine.pixoo_driver import PixooDriver
from utils.container_tree import print_layout_tree
from utils.logger import get_logger

logger = get_logger("PyXooEngine")


class PyXooEngine:
    """
    Runs the dashboard lifecycle: update, draw, and frame delivery.
    """

    def __init__(
            self,
            dashboard: Dashboard,
            driver: PixooDriver | None = None,
            frame_interval: float = 0.5,
            print_layout: bool = True):
        self.dashboard = dashboard
        self.driver = driver or PixooDriver()
        self.frame_interval = frame_interval
        self.print_layout = print_layout

        self.is_running = False
        self._is_closed = False
        self.frame_count = 0
        self.started_at: float | None = None
        self._last_tick = time.monotonic()

    def run_forever(self):
        """Starts the engine loop until stopped or interrupted."""
        self.start()

        try:
            while self.is_running:
                self.tick()
                self._sleep_until_next_frame()
        except KeyboardInterrupt:
            logger.info("Stopping...")
        finally:
            self.stop()

    def start(self):
        """Marks the engine as running and prints startup diagnostics."""
        if self.is_running:
            return

        self.is_running = True
        self.started_at = time.monotonic()
        self._last_tick = self.started_at

        logger.info(f"Engine loop started with {self.dashboard.widget_count} widgets.")
        if self.print_layout:
            print_layout_tree(self.dashboard)
        logger.info("Starting... Press CTRL + C to stop.")

    def stop(self):
        """Stops the engine and closes the frame driver."""
        if self._is_closed:
            return

        self.is_running = False
        self.driver.close()
        self._is_closed = True

        elapsed = self._elapsed_seconds()
        if elapsed > 0:
            logger.info(f"Engine stopped after {self.frame_count} frames in {elapsed:.1f}s.")
        else:
            logger.info(f"Engine stopped after {self.frame_count} frames.")

    def tick(self) -> bool:
        """Runs one update/draw/push cycle. Returns True when a frame was queued."""
        current_time = time.monotonic()
        dt = current_time - self._last_tick
        self._last_tick = current_time

        self.dashboard.update(dt)

        self.driver.clear()
        self.dashboard.draw(self.driver)

        queued = self.driver.push()
        self.frame_count += 1
        return queued

    def _sleep_until_next_frame(self):
        if self.frame_interval <= 0:
            return

        now = time.monotonic()
        sleep_time = self.frame_interval - (now % self.frame_interval)
        time.sleep(max(0, sleep_time))

    def _elapsed_seconds(self) -> float:
        if self.started_at is None:
            return 0.0

        return time.monotonic() - self.started_at
