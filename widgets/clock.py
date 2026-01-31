from datetime import datetime
from engine.widget import Widget
from engine.pixoo_driver import PixooDriver
from engine.font import Font

class ClockWidget(Widget):
    def __init__(self, x: int, y: int, font: Font, color:tuple[int, int, int] = (255, 255, 255)):
        super().__init__(x, y)
        self.font = font
        self.color = color

    def draw(self, driver: PixooDriver):
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")

        driver.draw_text(
            text=time_str,
            x=self.x,
            y=self.y,
            font=self.font,
            color=self.color
        )