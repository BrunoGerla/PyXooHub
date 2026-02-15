from widgets.text import TextWidget
from widgets.container import Container

from utils.logger import get_logger

logger = get_logger("LayoutTreeDebugger")

def print_layout_tree(widget, indent=0):
    # Create a visual tree structure
    prefix = "  " * indent + "└─ "
    
    # Get basic info
    name = widget.__class__.__name__
    props = f"(x={widget.x}, y={widget.y}, w={widget.width}, h={widget.height})"
    
    # Check for specific flags
    extra = ""
    if getattr(widget, "is_spacer", False):
        extra = " [SPACER]"
    elif isinstance(widget, TextWidget):
        extra = f" '{widget.text}'"
        
    print(f"{prefix}{name} {props}{extra}")

    # Recurse if it has children
    if isinstance(widget, Container):
        for child in widget.children:
            print_layout_tree(child, indent + 1)

def log_layout_tree(widget, indent=0):
    # Create a visual tree structure
    prefix = "  " * indent + "└─ "
    
    # Get basic info
    name = widget.__class__.__name__
    props = f"(x={widget.x}, y={widget.y}, w={widget.width}, h={widget.height})"
    
    # Check for specific flags
    extra = ""
    if getattr(widget, "is_spacer", False):
        extra = " [SPACER]"
    elif isinstance(widget, TextWidget):
        extra = f" '{widget.text}'"
        
    logger.info(f"{prefix}{name} {props}{extra}")

    # Recurse if it has children
    if isinstance(widget, Container):
        for child in widget.children:
            log_layout_tree(child, indent + 1)