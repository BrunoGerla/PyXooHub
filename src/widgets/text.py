from typing import Callable, Any

from engine.widget import Widget
from engine.pixoo_driver import PixooDriver
from engine.font import Font
from engine.color import Colors, ColorValue

from utils.logger import get_logger

logger = get_logger("TextWidget")

class TextWidget(Widget):
    """
    A widget that displays text. 
    Can be static (fixed string) or dynamic (updating through a data_source).
    """
    def __init__(
            self, 
            x: int = 0, 
            y: int = 0, 
            text: str = "",
            font: Font | None = None,
            color: ColorValue = Colors.WHITE, 
            character_spacing: int = 1, 
            space_size: int = 4,
            data_source: Callable[[], Any] | None = None,
            update_interval: float = 1.0,
            name: str | None = None,
            **kwargs):
        super().__init__(x, y, color, name, **kwargs)

        self.text = text
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

    @property
    def width(self) -> int:
        if not self.font or not self.text:
            return 0
        
        total_w = 0
        for char in self.text:
            if char == " ":
                total_w += self.space_size
                continue
        
            glyph = self.font.get_glyph(char)
            if glyph is None:
                continue

            total_w += glyph["width"] + self.char_spacing

        if self.text and self.text[-1] != " ":
            total_w = max(0, total_w - self.char_spacing)
        
        return total_w
    
    @width.setter
    def width(self, value):
        logger.warning("Attempted to manually set width of TextWidget. This is ignored because width is calculated dynamically.")

    @property
    def height(self) -> int:
        return 0 if not self.font or not self.text else self.font.height

    @height.setter
    def height(self, value):
        logger.warning("Attempted to manually set height of TextWidget. This is ignored because height is calculated dynamically.")

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

        if self.current_color is None:
            return
        
        driver.draw_text(
            text=self.text,
            x=self.x,
            y=self.y,
            font=self.font,
            color=self.current_color,
            character_spacing=self.char_spacing,
            space_size=self.space_size
        )
