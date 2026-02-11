from abc import ABC, abstractmethod
from engine.pixoo_driver import PixooDriver
from engine.color import Color, Colors, ColorValue
from utils.logger import get_logger

logger = get_logger("Widget")

class Widget(ABC):
    """
    Abstract Base Class for all widgets.
    Enforces that every widget must have an update and draw method.
    """
    def __init__(self, x: int, y: int, color: ColorValue = Colors.WHITE):
        self.x = x
        self.y = y
        
        self.color = self.parse_color(color)

    # TODO: Refactor to use Color.parse
    def parse_color(self, value, default = Colors.WHITE) -> Color:
        if isinstance(value, Color):
            return value
        if isinstance(value, (tuple, list)) and len(value) == 3:
            try:
                return Color(*value)
            except:
                logger.warning(f"Invalid Color Input: {value}. Using default")
                return default
        if isinstance(value, str):
            try:
                return Color.from_hex(value)
            except ValueError:
                logger.warning(f"Invalid hex color '{value}'. Using default.")
                return default
        else:
            logger.warning(f"Invalid Color Input Type: {type(value)}. Using default")
            return default

    @abstractmethod
    def update(self, dt: float):
        """
        Update the widget's state.
        dt: Delta Time in seconds (time since last frame)
        """

    @abstractmethod
    def draw(self, driver: PixooDriver):
        """
        Draws the widget content onto the driver's buffer.
        """
        pass