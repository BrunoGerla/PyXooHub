from abc import ABC, abstractmethod

class MouseProvider(ABC):
    """
    Abstract Class for Mouse Battery Providers
    """

    @abstractmethod
    def update(self, dt: float) -> bool:
        """
        Called every frame by the dashboard to handle background logic, 
        polling, or data fetching.
        """
        pass

    @property
    @abstractmethod
    def battery_percentage(self) -> float:
        """
        Pure getter. Should return a float between 0.0 and 1.0.
        If data is unavailable, return 0.0.
        """
        pass

    @property
    @abstractmethod
    def is_charging(self) -> bool:
        """
        Pure getter. Returns True if the mouse is currently plugged in/charging.
        """
        pass
