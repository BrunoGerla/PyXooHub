from typing import Callable, Any

from engine.widget import Widget
from engine.pixoo_driver import PixooDriver
from engine.font import Font

from utils.logger import get_logger

logger = get_logger("TextWidget")

class TextWidget(Widget):
    """
    A widget that displays text. 
    Can be static (fixed string) or dynamic (updating through a data_source).
    """
    def __init__(
            self, 
            x: int, 
            y: int, 
            text: str = "",
            font: Font | None = None, 
            color: tuple[int, int, int] = (255, 255, 255), 
            character_spacing: int = 1, 
            space_size: int = 4,
            data_source: Callable[[], Any] | None = None,
            update_interval: float = 1.0,
            **kwargs):
        super().__init__(x, y)

        self.text = text
        self.color = color
        self.char_spacing = character_spacing
        self.space_size = space_size
        
        if font is None:
            import resources 
            self.font = resources.small_font
        else:
            self.font = font

        self.data_source = data_source
        self.update_interval = update_interval
        self.timer = 0.0

        self._fetch_data()

    def update(self, dt: float):
        if self.data_source is None:
            return
        
        self.timer += dt

        if self.timer >= self.update_interval:
            self._fetch_data()
            self.timer -= self.update_interval

    def _fetch_data(self):
        if self.data_source is None:
            return
        
        try:
            new_value = self.data_source()
            self.text = str(new_value)
        except Exception as e:
            logger.error(f"Failed to fetch data and update text: {e}")
            self.text = "ERR"

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