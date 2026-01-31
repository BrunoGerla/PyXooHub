from engine.widget import Widget
from engine.pixoo_driver import PixooDriver
from engine.font import Font

class TextWidget(Widget):
    """
    A widget that displays a static string of text.
    """
    def __init__(self, text: str, x: int, y: int, font: Font, color: tuple[int, int, int] = (255, 255, 255)):
        super().__init__(x, y)
        self.text = text
        self.font = font
        self.color = color

    def draw(self, driver: PixooDriver):
        driver.draw_text(
            text=self.text,
            x=self.x,
            y=self.y,
            font=self.font,
            color=self.color
        )