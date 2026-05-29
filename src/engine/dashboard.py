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
        self._is_dirty = True

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty or any(widget.is_dirty for widget in self.widgets)

    def mark_dirty(self):
        self._is_dirty = True

    def mark_clean(self):
        self._is_dirty = False
        for widget in self.widgets:
            widget.mark_clean()

    @property
    def widget_count(self) -> int:
        """
        Returns the total number of widgets in the entire tree.
        """
        return sum(w.widget_count for w in self.widgets)
        
    def add_widget(self, widget: Widget):
        """Adds a widget to the dashboard."""
        self.widgets.append(widget)
        self.mark_dirty()

    def remove_widget(self, widget: Widget):
        """Removes a specific widget from the dashboard."""
        if widget in self.widgets:
            self.widgets.remove(widget)
            self.mark_dirty()

    def clear_widgets(self):
        """Removes all widgets."""
        self.widgets.clear()
        self.mark_dirty()

    def update(self, dt: float) -> bool:
        """Updates all of the widgets inside the Dashboard."""
        changed = False
        for widget in self.widgets:
            changed = bool(widget.update(dt)) or changed

        if changed:
            self.mark_dirty()

        return changed

    def draw(self, driver: PixooDriver):
        """Draws all of the widgets onto the selected driver's buffer."""
        driver.fill(self.background_color)
        
        for widget in self.widgets:
            widget.draw(driver)

        self.mark_clean()
