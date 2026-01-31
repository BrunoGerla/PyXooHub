from abc import ABC, abstractmethod
from engine.pixoo_driver import PixooDriver

class Widget(ABC):
    """
    Abastract Base Class for all widgets.
    Enforces that every widget MUST have a draw() method.
    """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def draw(self, driver: PixooDriver):
        """
        Draws the widget content onto the driver's buffer.
        """
        pass