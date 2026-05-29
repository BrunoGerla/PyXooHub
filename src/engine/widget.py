from abc import ABC, abstractmethod
from engine.pixoo_driver import PixooDriver
from engine.color import Color, ColorValue
from utils.logger import get_logger

logger = get_logger("Widget")

class Widget(ABC):
    """
    Abstract Base Class for all widgets.
    Enforces that every widget must have an update and draw method.
    """
    def __init__(self, x: int = 0, y: int = 0, color: ColorValue | None = None, name: str | None = None):
        self.name = name

        self._is_dirty = True
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0
        self._current_color: Color | None = None

        self.x = x
        self.y = y
        
        self.color = Color.parse(color) if color else None
        self.current_color = self.color

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    def mark_dirty(self):
        self._is_dirty = True

    def mark_clean(self):
        self._is_dirty = False

    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        if value != self._x:
            self.mark_dirty()
        self._x = value

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        if value != self._y:
            self.mark_dirty()
        self._y = value

    @property
    def current_color(self) -> Color | None:
        return self._current_color

    @current_color.setter
    def current_color(self, value: Color | None):
        if value != self._current_color:
            self._current_color = value
            self.mark_dirty()
    
    @width.setter
    def width(self, value: int):
        if value != self._width:
            self.mark_dirty()
        self._width = value

    @height.setter
    def height(self, value: int):
        if value != self._height:
            self.mark_dirty()
        self._height = value

    @property
    def widget_count(self) -> int:
        """
        Returns the number of widgets in this branch. 
        Base widgets count as 1.
        """
        return 1

    @property
    def size(self) -> tuple[int, int]:
        """Returns (width, height). Useful for layout math."""
        return self.width, self.height

    @abstractmethod
    def update(self, dt: float) -> bool | None:
        """
        Update the widget's state and effects.
        dt: Delta Time in seconds (time since last frame)
        """

    @abstractmethod
    def draw(self, driver: PixooDriver):
        """
        Draws the widget content onto the driver's buffer.
        """
