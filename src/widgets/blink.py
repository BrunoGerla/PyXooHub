from engine.color import Colors, ColorValue
from engine.pixoo_driver import PixooDriver
from engine.widget import Widget


class BlinkWidget(Widget):
    """
    A small blinking block for status/heartbeat indicators.
    """

    def __init__(
            self,
            x: int = 0,
            y: int = 0,
            width: int = 1,
            height: int = 1,
            color: ColorValue = Colors.GREEN,
            interval: float = 0.5,
            name: str | None = None):
        super().__init__(x=x, y=y, color=color, name=name)
        self.width = width
        self.height = height
        self.interval = interval
        self.timer = 0.0
        self.is_on = True

    def update(self, dt: float) -> bool:
        self.timer += dt
        if self.timer < self.interval:
            return False

        self.timer %= self.interval
        self.is_on = not self.is_on
        self.mark_dirty()
        return True

    def draw(self, driver: PixooDriver):
        if not self.is_on or self.current_color is None:
            return

        for px in range(self.width):
            for py in range(self.height):
                driver.set_pixel(self.x + px, self.y + py, self.current_color)
