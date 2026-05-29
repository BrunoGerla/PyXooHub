import requests
import time
from requests.exceptions import RequestException
import base64
import threading
from typing import Literal

import config
from engine.font import Font
from engine.color import Color
from utils.logger import get_logger
from utils.profiler import time_it

DriverColor = Color | tuple[int, int, int]
ResetReason = Literal["first frame", "periodic refresh", "reconnect", "manual policy"]

logger = get_logger("PixooDriver")

class PixooDriver:
    def __init__(
            self,
            ip_address: str = config.PIXOO_IP,
            port: int = config.PIXOO_PORT,
            retries: int = config.PIXOO_RETRIES,
            timeout: int = config.PIXOO_TIMEOUT,
            async_push: bool = config.PIXOO_ASYNC_PUSH,
            reset_policy: config.ResetPolicy = config.PIXOO_RESET_POLICY,
            reset_every_frames: int = config.PIXOO_RESET_EVERY_FRAMES,
            skip_unchanged_frames: bool = config.PIXOO_SKIP_UNCHANGED_FRAMES,
            status_log_interval: int = config.PIXOO_LOG_FRAME_STATUS_INTERVAL):
        self.ip: str = ip_address
        self.port: int = port
        self.retries: int = retries
        self.timeout: int = timeout
        self.base_url = f"http://{self.ip}:{self.port}/post"
        self.is_connected: bool = False

        self.session = requests.Session()

        # graphics engine
        self.width: int = 64
        self.height: int = 64
        self.frame_count: int = 1

        self.buffer = [0] * (self.width * self.height * 3)

        # frame delivery
        self.async_push = async_push
        self.reset_policy = reset_policy
        self.reset_every_frames = max(0, reset_every_frames)
        self.skip_unchanged_frames = skip_unchanged_frames
        self._needs_reset: bool = True
        self._frames_since_reset: int = 0
        self._last_submitted_frame: bytes | None = None
        self._sent_frames: int = 0
        self._skipped_frames: int = 0
        self._dropped_frames: int = 0
        self._failed_frames: int = 0
        self._duplicate_skip_announced: bool = False
        self._status_log_interval = max(0, status_log_interval)
        self._last_status_log_time = time.monotonic()
        self._last_status_sent_frames: int = 0
        self._last_status_skipped_frames: int = 0
        self._last_status_dropped_frames: int = 0
        self._last_status_failed_frames: int = 0

        self._condition = threading.Condition()
        self._pending_frame: bytes | None = None
        self._worker_busy: bool = False
        self._worker_stop: bool = False
        self._worker_thread: threading.Thread | None = None

        # initial connect
        self.connect()

        if self.async_push:
            self._start_worker()

    def connect(self) -> bool:
        """
        Attempts to establish a verified connection to the Pixoo
        """
        logger.info(f"Initiating handshake with Pixoo at {self.ip}:{self.port}")

        for attempt in range(1, self.retries + 1):
            if self._perform_handshake():
                self.is_connected = True
                self._needs_reset = True
                logger.info("Successfully connected to the Pixoo.")
                return True
            
            logger.warning(f"Connection attempt {attempt}/{self.retries} failed. Retrying in {self.timeout}s...")
            time.sleep(self.timeout)

        logger.critical(f"Failed to connect to Pixoo at {self.ip}. Is the IP correct?")
        self.is_connected = False
        return False

    def close(self, flush: bool = True):
        """Stops the async worker, optionally sending the newest queued frame first."""
        if not self.async_push or self._worker_thread is None:
            return

        with self._condition:
            if not flush:
                self._pending_frame = None
            self._worker_stop = True
            self._condition.notify_all()

        self._worker_thread.join(timeout=self.timeout + 1)
        if self._worker_thread.is_alive():
            logger.warning("Pixoo frame worker did not stop before timeout.")
        else:
            logger.info("Pixoo frame worker stopped.")
        
    # -- GRAPHICS ENGINE LOGIC --
    def clear(self):
        """Fills the buffer with black (0, 0, 0)"""
        self.buffer = [0] * (self.width * self.height * 3)

    def set_pixel(self, x: int, y: int, rgb: DriverColor):
        """
        Safely paints one pixel in the buffer.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        
        r, g, b = self._unpack_rgb(rgb)

        index = (y * self.width + x) * 3
        self.buffer[index : index+3] = (r, g, b)
        return
    
    def draw_text(self, text: str, x: int, y: int, font: Font, color: DriverColor, character_spacing: int = 1, space_size: int = 4):
        """
        Draws a string of text starting at (x, y).

        Args:
            text: The string to draw
            x: Starting X position
            y: Starting Y position
            font: An instance of the Font class
            rgb: Color tuple (R, G, B)
            character_spacing: Pixels between characters (default 1)
            space_size: Number for pixels used to represent a space
        """
        cursor_x : int = x

        for char in text:
            if char == " ":
                cursor_x += space_size
                continue

            glyph = font.get_glyph(char)

            if glyph is None:
                logger.warning(f"Char {char} not found in {font}")
                continue

            for px, py in glyph["pixels"]:
                self.set_pixel(cursor_x + px, y + py, color)

            cursor_x += glyph["width"] + character_spacing

    def fill(self, rgb: DriverColor):
        """Fills the screen with one color"""
        r, g, b = self._unpack_rgb(rgb)
        self.buffer = [r, g, b] * (self.width * self.height)
        
    def push(self) -> bool:
        """Queues the current buffer for delivery to the Pixoo."""
        frame = bytes(self.buffer)

        if self._should_skip_frame(frame):
            self._skipped_frames += 1
            self._log_duplicate_skip_once()
            self._log_status_if_due()
            return False

        self._last_submitted_frame = frame

        if not self.async_push:
            return self._send_frame(frame)

        with self._condition:
            if self._worker_thread is None or not self._worker_thread.is_alive():
                logger.warning("Pixoo async frame worker was not running. Restarting it now.")
                self._start_worker()

            if self._pending_frame is not None:
                self._dropped_frames += 1
                logger.debug("Replacing queued Pixoo frame with the newest frame.")

            self._pending_frame = frame
            self._condition.notify()

        return True

    @time_it(threshold_ms=350.0)
    def _send_frame(self, frame: bytes) -> bool:
        """Sends one frame to the Pixoo."""
        if not self.is_connected:
            logger.warning("Pixoo is disconnected. Trying to reconnect before sending a frame.")
            if not self.connect():
                return False

        if self._should_reset_before_push():
            reason = self._get_reset_reason()
            if not self._reset_http_gif_id(reason):
                return False

        pixel_data = base64.b64encode(frame).decode("utf-8")

        payload = {
            "Command": "Draw/SendHttpGif",
            "PicNum": 1,
            "PicWidth": self.width,
            "PicOffset": 0,
            "PicID": 1,
            "PicSpeed": 10,
            "PicData": pixel_data
        }

        try:
            logger.debug("Pushing request!")
            response = self.session.post(self.base_url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            self.is_connected = True
            self._sent_frames += 1
            self._frames_since_reset += 1

            if self._sent_frames == 1:
                mode = "async" if self.async_push else "sync"
                logger.info(f"First Pixoo frame sent ({mode}, reset policy: {self.reset_policy}).")

            self._log_status_if_due()
            return True
        except RequestException as e:
            self._failed_frames += 1
            logger.warning(f"Pixoo frame push failed: {e}")
            self.is_connected = False
            self._needs_reset = True
            return False

    def _start_worker(self):
        self._worker_thread = threading.Thread(
            target=self._frame_worker,
            name="PixooFrameWorker",
            daemon=True
        )
        self._worker_thread.start()
        logger.info("Pixoo async frame worker started.")

    def _frame_worker(self):
        while True:
            with self._condition:
                while self._pending_frame is None and not self._worker_stop:
                    self._condition.wait(timeout=0.5)

                if self._worker_stop and self._pending_frame is None:
                    return

                frame = self._pending_frame
                self._pending_frame = None
                self._worker_busy = True

            try:
                if frame is not None:
                    self._send_frame(frame)
            except Exception:
                self._failed_frames += 1
                self.is_connected = False
                self._needs_reset = True
                logger.error("Unexpected error in Pixoo async frame worker. The worker will keep running.")
                logger.debug("Pixoo async frame worker exception details.", exc_info=True)
            finally:
                with self._condition:
                    self._worker_busy = False
                    self._condition.notify_all()

    def _should_skip_frame(self, frame: bytes) -> bool:
        if not self.skip_unchanged_frames:
            return False

        if self._last_submitted_frame != frame:
            return False

        return self.is_connected and not self._needs_reset

    def _log_duplicate_skip_once(self):
        if self._duplicate_skip_announced:
            return

        logger.info("No pixel changes detected; skipping duplicate Pixoo frames until the dashboard changes.")
        self._duplicate_skip_announced = True

    def _log_status_if_due(self):
        if self._status_log_interval <= 0:
            return

        now = time.monotonic()
        if now - self._last_status_log_time < self._status_log_interval:
            return

        sent_delta = self._sent_frames - self._last_status_sent_frames
        skipped_delta = self._skipped_frames - self._last_status_skipped_frames
        dropped_delta = self._dropped_frames - self._last_status_dropped_frames
        failed_delta = self._failed_frames - self._last_status_failed_frames

        logger.info(
            f"Pixoo sender active ({now - self._last_status_log_time:.0f}s): "
            f"{sent_delta} sent, "
            f"{skipped_delta} unchanged skipped, "
            f"{dropped_delta} stale queued frames dropped, "
            f"{failed_delta} failed."
        )

        self._last_status_log_time = now
        self._last_status_sent_frames = self._sent_frames
        self._last_status_skipped_frames = self._skipped_frames
        self._last_status_dropped_frames = self._dropped_frames
        self._last_status_failed_frames = self._failed_frames

    def _should_reset_before_push(self) -> bool:
        if self.reset_policy == "never":
            return False

        if self.reset_policy == "always":
            return True

        if self._needs_reset:
            return True

        return (
            self.reset_policy == "periodic"
            and self.reset_every_frames > 0
            and self._frames_since_reset >= self.reset_every_frames
        )

    def _get_reset_reason(self) -> ResetReason:
        if self.reset_policy == "always":
            return "manual policy"

        if self._needs_reset and self._sent_frames == 0:
            return "first frame"

        if self._needs_reset:
            return "reconnect"

        return "periodic refresh"

    def _reset_http_gif_id(self, reason: ResetReason) -> bool:
        try:
            response = self.session.post(
                self.base_url,
                json={"Command": "Draw/ResetHttpGifId"},
                timeout=self.timeout
            )
            response.raise_for_status()
        except RequestException as e:
            self._failed_frames += 1
            logger.warning(f"Pixoo HTTP GIF reset failed: {e}")
            self.is_connected = False
            self._needs_reset = True
            return False

        self._needs_reset = False
        self._frames_since_reset = 0
        if reason in {"first frame", "reconnect"}:
            logger.info(f"Pixoo HTTP GIF slot reset ({reason}).")
        else:
            logger.debug(f"Pixoo HTTP GIF slot reset ({reason}).")

        return True

    # Helpers
    def _perform_handshake(self) -> bool:
        """
        Sends a harmless command to verify identity.
        """
        payload = {"Command": "Device/GetTime"}
        
        try:
            response = self.session.post(
                self.base_url, 
                json=payload, 
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.debug(f"Handshake rejected: HTTP {response.status_code}")
                return False
            
            try:
                response.json()
            except ValueError:
                logger.debug("Handshake rejected: Response was not valid JSON.")
                return False

            # we assume that if the request returns json we are connected to the Pixoo
            return True

        except RequestException as e:
            logger.debug(f"Handshake connection error: {e}")
            return False
        
    def _unpack_rgb(self, rgb: DriverColor) -> tuple[int, int, int]:
        r = self._clamp_value(rgb[0])
        g = self._clamp_value(rgb[1])
        b = self._clamp_value(rgb[2])
        return r, g, b

    def _clamp_value(self, value: int, min_val: int = 0, max_val: int = 255) -> int:
        return max(min_val, min(max_val, value))


if __name__ == "__main__":
    small_font = Font(str(config.ASSETS_PATH / "small"))
    print("starting")
    pixoo = PixooDriver()

    WHITE = (255, 255, 255)
    pixoo.clear()
    pixoo.set_pixel(10, 10, WHITE)
    pixoo.draw_text("TEST", 1, 20, small_font, (255, 0 , 0), space_size=1)
    pixoo.draw_text("11:53", 1, 26, small_font, (0, 255, 0))
    pixoo.push()
    pixoo.close()
