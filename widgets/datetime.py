from datetime import datetime
from engine.pixoo_driver import PixooDriver
from engine.font import Font
from widgets.text import TextWidget

class DateTimeWidget(TextWidget):
    def __init__(self, x: int, y: int, font: Font, 
                 color:tuple[int, int, int] = (255, 255, 255),
                 format: str = "%H:%M:%S",
                 update_interval: float = 1.0,
                 **kwargs):
        super().__init__(text="", x=x, y=y, font=font, color=color, **kwargs)

        self.format = format
        self.update_interval = update_interval

        self.timer = self.update_interval
        self.update(0.0)

    def update(self, dt: float):
        self.timer += dt

        if self.timer >= self.update_interval:
            self.text = datetime.now().strftime(self.format)

            self.timer -= self.update_interval