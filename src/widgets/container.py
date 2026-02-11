from abc import abstractmethod
from typing import Literal

from engine.pixoo_driver import PixooDriver
from engine.color import Color, Colors, ColorValue
from engine.widget import Widget

Alignment = Literal["left", "center", "right"]
VerticalAlignment = Literal["top", "center", "bottom"]


class Container(Widget):
    #TODO: WRITE DOCSTRING
    def __init__(self, x: int = 0, y: int = 0, children: list[Widget] | None = None, color: ColorValue | None = None):
        super().__init__(x, y, color)
        self.children = children or []

    def add_widget(self, widget: Widget):
        self.children.append(widget)
        self.reposition()

    def remove_widget(self, widget: Widget):
        self.children.remove(widget)
        self.reposition()

    @abstractmethod
    def reposition(self):
        """Must be implemented by subclasses to reposition children"""
        pass

    def update(self, dt: float):
        for child in self.children:
            child.update(dt)

    def draw(self, driver: PixooDriver):
        if self.color:
            for i in range(self.width):
                for j in range(self.height):
                    driver.set_pixel(self.x + i, self.y + j, self.color)

        for child in self.children:
            child.draw(driver)


class VerticalContainer(Container):
    #TODO: WRITE DOCSTRING
    def __init__(
            self, 
            x: int = 0, 
            y: int = 0, 
            width: int = 64,
            fixed_height: int | None = None,
            padding: int = 0,
            spacing: int = 1,
            children: list[Widget] | None = None,
            align: Alignment = "left",
            color: ColorValue | None = None):
        super().__init__(x, y, children, color)
        self.width = width
        self.padding = padding
        self.spacing = spacing
        self._align: Alignment = align

        self._fixed_height = fixed_height

        self.reposition()

    @property
    def height(self) -> int:
        if self._fixed_height and self._fixed_height > 0:
            return self._fixed_height
        return max(0, 64 - self.y)
    
    @height.setter
    def height(self, value):
        self._fixed_height = value
        self.reposition()
        

    def reposition(self):
        """Stacks children vertically."""
        content_height = self._get_content_height()
        self._set_spacer_height(content_height)
        
        current_y = self.y + self.padding

        for child in self.children:
            if self._align == "center":
                child.x = self.x + (self.width - child.width) // 2
            elif self._align == "right":
                child.x = self.x + self.width - child.width - self.padding
            else:
                child.x = self.x + self.padding

            child.y = current_y
            
            if isinstance(child, Container):
                child.reposition()
                
            current_y += child.height + self.spacing

    def _get_content_height(self) -> int:
        if not self.children:
            return 0
        
        content_height = sum(
            c.height for c in self.children if not getattr(c, 'is_spacer', False)
        )

        content_height += self.spacing * (len(self.children) -1)
        content_height += self.padding * 2
        return content_height
    
    def _set_spacer_height(self, used_height: int):
        spacers = [c for c in self.children if getattr(c, 'is_spacer', False)]
        if spacers:
            remaining_space = max(0, self.height - used_height)
            space_per_spacer = remaining_space // len(spacers)

            for spacer in spacers:
                spacer.height = space_per_spacer



class HorizontalContainer(Container):
    #TODO: WRITE DOCSTRING
    def __init__(
            self, 
            x: int = 0, 
            y: int = 0, 
            width: int | None = None, # None = Flex to edge
            height: int = 10,         # Fixed height for the row
            padding: int = 0,
            spacing: int = 1,
            children: list[Widget] | None = None,
            align: VerticalAlignment = "top",
            color: ColorValue | None = None):
        super().__init__(x, y, children, color)
        self.height = height
        self.padding = padding
        self.spacing = spacing
        self._align: VerticalAlignment = align

        self._fixed_width = width

        self.reposition()

    @property
    def width(self) -> int:
        if self._fixed_width and self._fixed_width > 0:
            return self._fixed_width
        return max(0, 64 - self.x)
    
    @width.setter
    def width(self, value):
        self._fixed_width = value
        self.reposition()
        
    def reposition(self):
        """Stacks children horizontally."""
        content_width = self._get_content_width()
        self._set_spacer_width(content_width)
        
        current_x = self.x + self.padding

        for child in self.children:
            # Vertical Alignment Logic (Cross-Axis)
            if self._align == "center":
                child.y = self.y + (self.height - child.height) // 2
            elif self._align == "bottom":
                child.y = self.y + self.height - child.height - self.padding
            else: # top
                child.y = self.y + self.padding

            # Horizontal Stacking (Main-Axis)
            child.x = current_x
            
            if isinstance(child, Container):
                child.reposition()
                
            current_x += child.width + self.spacing

    def _get_content_width(self) -> int:
        if not self.children:
            return 0
        
        content_width = sum(
            c.width for c in self.children if not getattr(c, 'is_spacer', False)
        )

        content_width += self.spacing * (len(self.children) - 1)
        content_width += self.padding * 2
        return content_width
    
    def _set_spacer_width(self, used_width: int):
        spacers = [c for c in self.children if getattr(c, 'is_spacer', False)]
        if spacers:
            remaining_space = max(0, self.width - used_width)
            space_per_spacer = remaining_space // len(spacers)

            for spacer in spacers:
                spacer.width = space_per_spacer