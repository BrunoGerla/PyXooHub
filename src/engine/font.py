import os
from typing import TypedDict

from PIL import Image

from utils.logger import get_logger

logger = get_logger("Font Engine")


class GlyphData(TypedDict):
    width: int
    height: int
    pixels: list[tuple[int, int]]

class Font:
    def __init__(self, folder_path: str):
        self._glyphs = {}
        self._max_height = 0
        self._load_fonts(folder_path)

    @property
    def height(self) -> int:
        return self._max_height

    def _load_fonts(self, folder: str):
        if not os.path.exists(folder):
            logger.error(f"Error: Font folder {folder} not found.")
            return
        
        for filename in os.listdir(folder):
            if not filename.endswith(".png"):
                continue

            try:
                ascii_code = int(filename.split(".")[0])
                char = chr(ascii_code)
            except ValueError:
                logger.warning(f"Warning: Parsing {filename} didn't work.")
                continue

            path = os.path.join(folder, filename)

            with Image.open(path).convert("RGBA") as img:
                glyph_data = self._extract_glyph_data(img)
                self._glyphs[char] = glyph_data

                if glyph_data["height"] > self._max_height:
                    self._max_height = glyph_data["height"]

    def _extract_glyph_data(self, img: Image.Image) -> GlyphData:
        """
        Scans image for visible pixels.
        output is a dict of width, height and pixels
        """
        visible_pixels: list[tuple[int, int]] = []

        for y in range(img.height):
            for x in range(img.width):
                pixel_values: tuple[int, int, int, int] = img.getpixel((x, y)) # type: ignore
                r, g, b, a = pixel_values

                is_not_black = (r > 0 or g > 0 or b > 0)
                if is_not_black:
                    visible_pixels.append((x, y))

        return {
            "width": img.width,
            "height": img.height,
            "pixels": visible_pixels
        }

    def get_glyph(self, char) -> GlyphData | None:
        """
        Retrieves the glyph data for a character.
        If the character is missing, falls back to '?' (ASCII 63)
        If '?' is also missing, return None.
        """
        if char in self._glyphs:
            return self._glyphs.get(char)
        
        logger.warning(f"Warning: Glyph for '{char}' not found. Using fallback.")

        return self._glyphs.get("?")