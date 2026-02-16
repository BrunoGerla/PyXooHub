from engine.dashboard import Dashboard
from widgets.container import Container
from widgets.text import TextWidget
from utils.logger import get_logger

logger = get_logger("LayoutTree")

def print_layout_tree(node, indent=0):
    """
    Recursively logs the structure of a Dashboard or Widget tree.
    Can accept a Dashboard object OR a Widget object.
    """
    prefix = "  " * indent + "└─ "

    if isinstance(node, Dashboard):
        logger.info(f"{prefix}Dashboard (Bg: {node.background_color})")
        logger.info(f"{'  ' * (indent+1)}└─ Total Widgets: {node.widget_count}")
        
        for child in node.widgets:
            print_layout_tree(child, indent + 1)
        return

    name = node.__class__.__name__
    props = f"(x={node.x}, y={node.y}, w={node.width}, h={node.height})"
    
    extra = ""
    if getattr(node, "is_spacer", False):
        extra = " [SPACER]"
    elif isinstance(node, TextWidget):
        extra = f" '{node.text}'"
        
    logger.info(f"{prefix}{name} {props}{extra}")

    if isinstance(node, Container):
        for child in node.children:
            print_layout_tree(child, indent + 1)