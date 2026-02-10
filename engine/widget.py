from abc import ABC, abstractmethod
from engine.pixoo_driver import PixooDriver

class Widget(ABC):
    """
    Abstract Base Class for all widgets.
    Enforces that every widget must have an update and draw method.
    """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

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