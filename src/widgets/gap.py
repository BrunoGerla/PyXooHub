from engine.widget import Widget

class Gap(Widget):
    """
    A fixed-size  empty widget.
    """
    def __init__(self, size: int):
        super().__init__()
        self.width = size
        self.height = size

    def update(self, dt: float) -> bool:
        return False

    def draw(self, driver):
        pass
