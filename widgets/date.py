from datetime import datetime
from engine.widget import Widget
from engine.pixoo_driver import PixooDriver
from engine.font import Font

class DateWidget(Widget):
    def __init__(self, x: int, y: int,  font: Font, date_format: str = "%d-%m-%Y", color: tuple[int, int, int] = (255, 255, 255)):
        super().__init__(x, y)
        self.font = font
        self.color = color
        self.date_format = date_format

    def draw(self, driver: PixooDriver):
        now = datetime.now()
        date_str = now.strftime(self.date_format)

        driver.draw_text(
            text=date_str,
            x=self.x,
            y=self.y,
            font=self.font,
            color=self.color
        )