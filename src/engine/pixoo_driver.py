import requests
import time
from requests.exceptions import RequestException
import base64

import config
from engine.font import Font
from utils.logger import get_logger, configure_logging


configure_logging()
logger = get_logger("PixooDriver")


class PixooDriver:
    def __init__(self, ip_address: str = config.PIXOO_IP, port: int = config.PIXOO_PORT, retries: int = config.PIXOO_RETRIES, timeout: int = config.PIXOO_TIMEOUT):
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

        # initial connect
        self.connect()

    def connect(self) -> bool:
        """
        Attempts to establish a verified connection to the Pixoo
        """
        logger.info(f"Initiating handshake with Pixoo at {self.ip}:{self.port}")

        for attempt in range(1, config.PIXOO_RETRIES + 1):
            if self._perform_handshake():
                self.is_connected = True
                logger.info(f"Succesfully connected to the Pixoo!")
                return True
            
            logger.warning(f"Connection attempt {attempt}/{config.PIXOO_RETRIES} failed. Retrying in 1s...")
            time.sleep(self.timeout)

        logger.critical(f"Failed to connect to Pixoo at {self.ip}. Is the IP correct?")
        self.is_connected = False
        return False
        
    # -- GRAPHICS ENGINE LOGIC --
    def clear(self):
        """Fills the buffer with black (0, 0, 0)"""
        self.buffer = [0] * (self.width * self.height * 3)

    def set_pixel(self, x: int, y: int, rgb: tuple[int, int, int]):
        """
        Safely paints one pixel in the buffer.
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        
        r, g, b = self._unpack_rgb(rgb)

        index = (y * self.width + x) * 3
        self.buffer[index : index+3] = (r, g, b)
        return
    
    def draw_text(self, text: str, x: int, y: int, font: Font, color: tuple[int, int, int], character_spacing: int = 1, space_size: int = 4):
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

    def fill(self, rgb: tuple[int, int, int]):
        """Fills the screen with one color"""
        r, g, b = self._unpack_rgb(rgb)
        self.buffer = [r, g, b] * (self.width * self.height)
        
    def push(self):
        """Sends the buffer to the Pixoo"""
        if not self.is_connected:
            logger.warning("Cannot push frame: Device disconnected.")
            return

        try:
            self.session.post(self.base_url, json={"Command": "Draw/ResetHttpGifId"}, timeout=self.timeout)
        except Exception:
            pass

        pixel_data = base64.b64encode(bytes(self.buffer)).decode('utf-8')

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
            self.session.post(self.base_url, json=payload, timeout=config.PIXOO_TIMEOUT)
        except Exception as e:
            logger.error(f"Push failed: {e}")
            self.is_connected = False

    # Helpers
    def _perform_handshake(self) -> bool:
        """
        Sends a harmless command to verify identity.
        """
        payload = {"Command": "Device/GetTime"}
        
        try:
            response = requests.post(
                self.base_url, 
                json=payload, 
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.debug(f"Handshake rejected: HTTP {response.status_code}")
                return False
            
            try:
                data = response.json()
            except ValueError:
                logger.debug("Handshake rejected: Response was not valid JSON.")
                return False

            # we assume that if the request returns json we are connected to the Pixoo
            return True

        except RequestException as e:
            logger.debug(f"Handshake connection error: {e}")
            return False
        
    def _unpack_rgb(self, rgb: tuple[int, int, int]) -> tuple[int, int, int]:
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
