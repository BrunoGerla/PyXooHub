import math
from typing import Callable, Any

from engine.widget import Widget
from engine.pixoo_driver import PixooDriver
from engine.color import Color, Colors, ColorValue

from utils.logger import get_logger

logger = get_logger("BarWidget")

class BarWidget(Widget):
    """
    A widget that displays a progress bar.
    Can be static (fixed percentage) or dynamic (polling a data_source).
    """
    def __init__(self, 
                 width: int, 
                 height: int,
                 x: int = 0, 
                 y: int = 0,  
                 percentage: float = 0.0,
                 color: ColorValue = Colors.WHITE,
                 outline: bool = True,
                 outline_color: ColorValue = Colors.WHITE,
                 color_map: dict[float, ColorValue] | None = None,
                 steps: int = 1, 
                 data_source: Callable[[], Any] | None = None,
                 update_interval: float = 1.0,
                 name: str | None = None):
        """
        Args:
            color_map: A dictionary of {upper_limit: ColorValue}.
        """
        super().__init__(x, y, color, name)
        self.width = width
        self.height = height
        self.percentage = self._clamp_percentage(percentage)

        self.default_color = Color.parse(color)
        self.current_color: Color = self.default_color
        self.outline = outline
        self.outline_color = Color.parse(outline_color)
        self.color_map = dict(sorted(color_map.items())) if color_map else None

        self.steps = steps

        self.data_source = data_source
        self.update_interval = update_interval
        self.timer = self.update_interval

        if self.data_source:
            self.update(0.0)
        else:
            self._update_color()

    def set_percentage(self, percentage: float):
        """Updates the bar's percentage (0.0 to 1.0)"""
        self.percentage = self._clamp_percentage(percentage)
        self._update_color()

    def update(self, dt: float):
        if self.data_source is None:
            return
        
        self.timer += dt

        if self.timer >= self.update_interval:
            value = self._fetch_data()

            if value is not None:
                self.set_percentage(value)
            else:
                self.percentage = 1
                self.current_color = Colors.RED

            self.timer -= self.update_interval

    def _fetch_data(self) -> float | None:
        if self.data_source is None:
            return
        
        try:
            return float(self.data_source())
        except Exception as e:
            logger.error(f"Failed to fetch data for BarWidget: {e}")
            return None

    def _update_color(self):
        """Determines the current color based on the color_map."""
        if not self.color_map:
            self.current_color = self.default_color
            return
        
        for threshold, color in self.color_map.items():
            if self.percentage <= threshold:
                self.current_color = Color.parse(color)
                return
            
        self.current_color = self.default_color

    def draw(self, driver: PixooDriver):
        # determine orientation. If square, we still want to load bottom to top.
        is_vertical = self.height >= self.width

        start_x, start_y = self.x, self.y
        draw_w, draw_h = self.width, self.height

        if self.outline:
            # Draw top and bottom horizontal lines
            for i in range(draw_w):
                driver.set_pixel(start_x + i, start_y, self.outline_color)
                driver.set_pixel(start_x + i, start_y + draw_h - 1, self.outline_color)
            
            # Draw left and right vertical lines
            for i in range(draw_h):
                driver.set_pixel(start_x, start_y + i, self.outline_color)
                driver.set_pixel(start_x + draw_w - 1, start_y + i, self.outline_color)
            
            # Adjust the "inner" area where the bar will actually fill
            fill_x = start_x + 1
            fill_y = start_y + 1
            fill_w = max(0, draw_w - 2)
            fill_h = max(0, draw_h - 2)

        else:
            # No outline, use the full area
            fill_x, fill_y = start_x, start_y
            fill_w, fill_h = draw_w, draw_h

        if fill_w <= 0 or fill_h <= 0: return
        
        if is_vertical:
            total_pixels = fill_h * self.percentage
            full_pixels, remainder = self._calculate_steps(total_pixels)

            # draw the full pixels first
            for py in range(full_pixels):
                # Calculate Y: Bottom of fill area - current offset
                pixel_y = (fill_y + fill_h - 1) - py
                for px in range(fill_w):
                    driver.set_pixel(fill_x + px, pixel_y, self.current_color)
            
            # draw the dimmed pixels
            if remainder > 0.05:
                dimmed_color = self.current_color * remainder
                pixel_y = (fill_y + fill_h - 1) - full_pixels
                if pixel_y >= fill_y:
                    for px in range(fill_w):
                        driver.set_pixel(fill_x + px, pixel_y, dimmed_color)

        if not is_vertical:
            # Horizontal: Fill from left to right
            total_pixels = fill_w * self.percentage
            full_pixels, remainder = self._calculate_steps(total_pixels)
            
            # draw full pixels first
            for px in range(full_pixels):
                pixel_x = fill_x + px
                for py in range(fill_h):
                    driver.set_pixel(pixel_x, fill_y + py, self.current_color)

            # draw the dimmed pixels
            if remainder > 0.05:
                dimmed_color = self.current_color * remainder
                pixel_x = fill_x + full_pixels
                if pixel_x < fill_x + fill_w:
                    for py in range(fill_h):
                        driver.set_pixel(pixel_x, fill_y + py, dimmed_color)

    def _calculate_steps(self, total_pixels: float) -> tuple[int, float]:
        """
        Returns (full_pixels, remainder_brightness) based on self.steps.
        """
        EPSILON = 1e-5
        if self.steps <= EPSILON:
            full = int(total_pixels)
            rem = total_pixels - full
            return full, rem
        
        full = int(total_pixels)
        raw_remainder = total_pixels - full

        if raw_remainder <= EPSILON:
            return full, 0.0
        
        snapped_remainder = math.ceil((raw_remainder - EPSILON)* self.steps) / self.steps

        return full, snapped_remainder

    def _clamp_percentage(self, value: float) -> float:
        return min(1, max(0, value))