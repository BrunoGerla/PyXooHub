from engine.widget import Widget
from engine.pixoo_driver import PixooDriver
from engine.font import Font

class TextWidget(Widget):
    """
    A widget that displays a static string of text.
    """
    def __init__(
            self, 
            text: str, 
            x: int, 
            y: int, 
            font: Font, 
            color: tuple[int, int, int] = (255, 255, 255), 
            character_spacing: int = 1, 
            space_size: int = 4,
            **kwargs):
        super().__init__(x, y)

        self.text = text
        self.font = font
        self.color = color
        self.char_spacing = character_spacing
        self.space_size = space_size

    def update(self, dt: float):
        pass

    def draw(self, driver: PixooDriver):
        """
        Renders the current value of self.text.
        """
        driver.draw_text(
            text=self.text,
            x=self.x,
            y=self.y,
            font=self.font,
            color=self.color,
            character_spacing=self.char_spacing,
            space_size=self.space_size
        )