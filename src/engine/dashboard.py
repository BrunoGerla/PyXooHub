from engine.pixoo_driver import PixooDriver
from engine.widget import Widget
from engine.color import Color, Colors, ColorValue

class Dashboard:
    """
    A container that manages a collection of widgets.
    Handles updating, drawing, and lifecycle management of its children.
    """
    def __init__(self, widgets: list[Widget] = [], background_color: ColorValue = Colors.BLACK):
        self.widgets: list[Widget] = widgets
        self.background_color: Color = Color.parse(background_color)
        
    def add_widget(self, widget: Widget):
        """Adds a widget to the dashboard."""
        self.widgets.append(widget)

    def remove_widget(self, widget: Widget):
        """Removes a specific widget from the dashboard."""
        if widget in self.widgets:
            self.widgets.remove(widget)

    def clear_widgets(self):
        """Removes all widgets."""
        self.widgets.clear()

    def update(self, dt: float):
        """Updates all of the widgets inside the Dashboard."""
        for widget in self.widgets:
            widget.update(dt)

    def draw(self, driver: PixooDriver):
        """Draws all of the widgets onto the selected driver's buffer."""
        driver.fill(self.background_color)
        
        for widget in self.widgets:
            widget.draw(driver)