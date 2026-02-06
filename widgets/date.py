from datetime import datetime
from engine.pixoo_driver import PixooDriver
from engine.font import Font
from widgets.text import TextWidget

class DateWidget(TextWidget):
    def __init__(self, x: int, y: int, font: Font, 
            color:tuple[int, int, int] = (255, 255, 255),
            date_format: str = "%d-%m-%Y",
            **kwargs):
        super().__init__(text="", x=x, y=y, font=font, color=color, **kwargs)
        
        self.date_format = date_format
        self.update(0.0)

    def update(self, dt: float):
        now = datetime.now()
        self.text = now.strftime(self.date_format)