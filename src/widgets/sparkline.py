import math

from engine.color import Colors, ColorValue
from engine.pixoo_driver import PixooDriver
from engine.widget import Widget


class SparklineWidget(Widget):
    """
    A tiny animated waveform/status sparkline.
    """

    def __init__(
            self,
            x: int = 0,
            y: int = 0,
            width: int = 16,
            height: int = 5,
            color: ColorValue = Colors.CYAN,
            interval: float = 0.2,
            name: str | None = None):
        super().__init__(x=x, y=y, color=color, name=name)
        self.width = width
        self.height = height
        self.interval = interval
        self.timer = 0.0
        self.phase = 0

    def update(self, dt: float) -> bool:
        self.timer += dt
        if self.timer < self.interval:
            return False

        self.timer %= self.interval
        self.phase = (self.phase + 1) % max(1, self.width)
        self.mark_dirty()
        return True

    def draw(self, driver: PixooDriver):
        if self.current_color is None or self.height <= 0:
            return

        center_y = self.y + self.height // 2
        amplitude = max(1, self.height // 2)

        for px in range(self.width):
            wave = math.sin((px + self.phase) * 0.9)
            py = center_y + int(round(wave * amplitude))
            driver.set_pixel(self.x + px, py, self.current_color)
