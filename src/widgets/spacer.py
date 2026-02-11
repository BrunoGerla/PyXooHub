from engine.widget import Widget

class Spacer(Widget):
    """
    An invisible widget that expands to fill remaining space in a Container.
    """
    def __init__(self):
        super().__init__(0, 0)
        self.is_spacer = True
    
    def update(self, dt: float):
        pass

    def draw(self, driver):
        pass