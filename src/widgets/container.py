from abc import abstractmethod
from typing import Literal

from engine.pixoo_driver import PixooDriver
from engine.color import ColorValue
from engine.widget import Widget

Alignment = Literal["left", "center", "right"]
VerticalAlignment = Literal["top", "center", "bottom"]


class Container(Widget):
    """
    Base class for layout containers.
    """
    def __init__(self, x: int = 0, y: int = 0, children: list[Widget] | None = None, color: ColorValue | None = None, autosize: bool = True, name: str | None = None):
        super().__init__(x, y, color, name=name)
        self.children = children or []
        self.autosize = autosize

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty or any(child.is_dirty for child in self.children)

    def mark_clean(self):
        super().mark_clean()
        for child in self.children:
            child.mark_clean()

    @property
    def widget_count(self) -> int:
        """
        Recursive count: 1 (Self) + Sum(Children)
        """
        return 1 + sum(child.widget_count for child in self.children)

    def add_widget(self, widget: Widget):
        self.children.append(widget)
        self.reposition()
        self.mark_dirty()

    def remove_widget(self, widget: Widget):
        self.children.remove(widget)
        self.reposition()
        self.mark_dirty()

    @abstractmethod
    def reposition(self):
        """Must be implemented by subclasses to reposition children"""
        pass

    def update(self, dt: float) -> bool:
        changed = False
        for child in self.children:
            changed = bool(child.update(dt)) or changed

        if changed:
            self.mark_dirty()

        return changed

    def draw(self, driver: PixooDriver):
        if self.color:
            for i in range(self.width):
                for j in range(self.height):
                    driver.set_pixel(self.x + i, self.y + j, self.color)

        for child in self.children:
            child.draw(driver)


class VerticalContainer(Container):
    def __init__(
            self, 
            x: int = 0, 
            y: int = 0, 
            width: int | None = None,
            fixed_height: int | None = None,
            padding: int = 0,
            spacing: int = 1,
            children: list[Widget] | None = None,
            align: Alignment = "left",
            color: ColorValue | None = None,
            autosize: bool = True,
            name: str | None = None):
        super().__init__(x, y, children, color, autosize, name)
        self.padding = padding
        self.spacing = spacing
        self._align: Alignment = align

        self._fixed_height = fixed_height
        self._fixed_width = width

        self.reposition()

    @property
    def height(self) -> int:
        if self._fixed_height is not None:
            return self._fixed_height
        
        if self.autosize:
            return self._get_content_height()
        
        return max(0, 64 - self.y)
    
    @height.setter
    def height(self, value):
        self._fixed_height = value
        self.reposition()

    @property
    def width(self) -> int:
        if self._fixed_width is not None:
            return self._fixed_width
        
        if self.autosize:
            if not self.children:
                return 0
            content_width = max((c.width for c in self.children if not getattr(c, 'is_spacer', False)), default=0)
            return content_width + (self.padding * 2)
    
        return max(0, 64 - self.x)
    
    @width.setter
    def width(self, value):
        self._fixed_width = value
        self.reposition()
        
    def reposition(self):
        """Stacks children vertically."""
        changed = False
        content_height = self._get_content_height()
        changed = self._set_spacer_height(content_height) or changed
        
        current_y = self.y + self.padding

        for i, child in enumerate(self.children):
            previous_position = (child.x, child.y)
            if self._align == "center":
                child.x = self.x + (self.width - child.width) // 2
            elif self._align == "right":
                child.x = self.x + self.width - child.width - self.padding
            else:
                child.x = self.x + self.padding

            child.y = current_y

            if (child.x, child.y) != previous_position:
                child.mark_dirty()
                changed = True
            
            if isinstance(child, Container):
                child.reposition()
                
            current_y += child.height
            
            # Smart spacing: only add gap if between two solid widgets
            is_this_spacer = getattr(child, 'is_spacer', False)
            if i + 1 < len(self.children):
                is_next_spacer = getattr(self.children[i+1], 'is_spacer', False)
                if not is_this_spacer and not is_next_spacer:
                    current_y += self.spacing

        if changed:
            self.mark_dirty()

    def _get_content_height(self) -> int:
        if not self.children:
            return 0
        
        content_height = sum(c.height for c in self.children if not getattr(c, 'is_spacer', False))

        # Count how many smart gaps we actually have
        spacing_count = 0
        for i, child in enumerate(self.children):
            if i + 1 < len(self.children):
                is_this_spacer = getattr(child, 'is_spacer', False)
                is_next_spacer = getattr(self.children[i+1], 'is_spacer', False)
                if not is_this_spacer and not is_next_spacer:
                    spacing_count += 1
                    
        content_height += self.spacing * spacing_count
        content_height += self.padding * 2
        return content_height
    
    def _set_spacer_height(self, used_height: int) -> bool:
        changed = False
        spacers = [c for c in self.children if getattr(c, 'is_spacer', False)]
        if spacers:
            remaining_space = max(0, self.height - used_height)
            space_per_spacer = remaining_space // len(spacers)

            for spacer in spacers:
                if spacer.height != space_per_spacer:
                    spacer.height = space_per_spacer
                    spacer.mark_dirty()
                    changed = True

        return changed


class HorizontalContainer(Container):
    def __init__(
            self, 
            x: int = 0, 
            y: int = 0, 
            width: int | None = None, # None = Flex to edge
            height: int | None = None,
            padding: int = 0,
            spacing: int = 1,
            children: list[Widget] | None = None,
            align: VerticalAlignment = "top",
            color: ColorValue | None = None,
            autosize: bool = True,
            name: str | None = None):
        super().__init__(x, y, children, color, autosize, name)
        self.padding = padding
        self.spacing = spacing
        self._align: VerticalAlignment = align

        self._fixed_width = width
        self._fixed_height = height

        self.reposition()

    @property
    def width(self) -> int:
        if self._fixed_width is not None:
            return self._fixed_width
        
        if self.autosize:
            return self._get_content_width()
        
        return max(0, 64 - self.x)
    
    @width.setter
    def width(self, value):
        self._fixed_width = value
        self.reposition()

    @property
    def height(self) -> int:
        if self._fixed_height is not None:
            return self._fixed_height
        
        if self.autosize:
            if not self.children:
                return 0
            content_height = max((c.height for c in self.children if not getattr(c, 'is_spacer', False)), default=0)
            return content_height + (self.padding * 2)
        
        return max(0, 64 - self.y)
        
    @height.setter
    def height(self, value):
        self._fixed_height = value   # <--- FIXED TYPO HERE!
        self.reposition()
            
    def reposition(self):
        """Stacks children horizontally."""
        changed = False
        content_width = self._get_content_width()
        changed = self._set_spacer_width(content_width) or changed
        
        current_x = self.x + self.padding

        for i, child in enumerate(self.children):
            previous_position = (child.x, child.y)
            # Vertical Alignment Logic (Cross-Axis)
            if self._align == "center":
                child.y = self.y + (self.height - child.height) // 2
            elif self._align == "bottom":
                child.y = self.y + self.height - child.height - self.padding
            else: # top
                child.y = self.y + self.padding

            # Horizontal Stacking (Main-Axis)
            child.x = current_x

            if (child.x, child.y) != previous_position:
                child.mark_dirty()
                changed = True
            
            if isinstance(child, Container):
                child.reposition()
                
            current_x += child.width
            
            # Smart spacing: only add gap if between two solid widgets
            is_this_spacer = getattr(child, 'is_spacer', False)
            if i + 1 < len(self.children):
                is_next_spacer = getattr(self.children[i+1], 'is_spacer', False)
                if not is_this_spacer and not is_next_spacer:
                    current_x += self.spacing

        if changed:
            self.mark_dirty()

    def _get_content_width(self) -> int:
        if not self.children:
            return 0
        
        content_width = sum(c.width for c in self.children if not getattr(c, 'is_spacer', False))

        # Count how many smart gaps we actually have
        spacing_count = 0
        for i, child in enumerate(self.children):
            if i + 1 < len(self.children):
                is_this_spacer = getattr(child, 'is_spacer', False)
                is_next_spacer = getattr(self.children[i+1], 'is_spacer', False)
                if not is_this_spacer and not is_next_spacer:
                    spacing_count += 1
                    
        content_width += self.spacing * spacing_count
        content_width += self.padding * 2
        return content_width
    
    def _set_spacer_width(self, used_width: int) -> bool:
        changed = False
        spacers = [c for c in self.children if getattr(c, 'is_spacer', False)]
        if spacers:
            remaining_space = max(0, self.width - used_width)
            space_per_spacer = remaining_space // len(spacers)

            for spacer in spacers:
                if spacer.width != space_per_spacer:
                    spacer.width = space_per_spacer
                    spacer.mark_dirty()
                    changed = True

        return changed
