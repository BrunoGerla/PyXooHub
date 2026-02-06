from abc import ABC, abstractmethod

class MouseProvider(ABC):
    """
    Abstract Class for Mouse Battery Providers
    """

    @abstractmethod
    def get_battery_percentage(self) -> float:
        """
        Should return a float between 0.0 and 1.0.
        If data is unavailable, return 0.0.
        """
        pass