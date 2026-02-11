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
    def __init__(self, x: int = 0, y: int = 0, color: ColorValue = Colors.WHITE):
        self.x = x
        self.y = y

        self._width = 0
        self._height = 0
        
        self.color = Color.parse(color)
        self.current_color = self.color

    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @width.setter
    def width(self, value: int):
        self._width = value

    @height.setter
    def height(self, value: int):
        self._height = value

    @property
    def size(self) -> tuple[int, int]:
        """Returns (width, height). Useful for layout math."""
        return self.width, self.height

    @abstractmethod
    def update(self, dt: float):
        """
        Update the widget's state and effects.
        dt: Delta Time in seconds (time since last frame)
        """

    @abstractmethod
    def draw(self, driver: PixooDriver):
        """
        Draws the widget content onto the driver's buffer.
        """