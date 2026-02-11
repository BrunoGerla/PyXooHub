from engine.dashboard import Dashboard
from engine.color import Colors, Color
import resources

# Widgets
from widgets.text import TextWidget
from widgets.datetime import DateTimeWidget
from widgets.bar import BarWidget

def build_cyberpunk_dashboard() -> Dashboard:
    """
    A Cyberpunk-themed 'System Monitor' default dashboard.
    Static version (no animation tags).
    """
    bg_color = Color(10, 15, 30)
    
    # --- WIDGET DEFINITIONS ---
    header_label = TextWidget(text="SYS.RDY", x=2, y=2, font=resources.small_font, color=Colors.CYAN)
    
    header_line = BarWidget(x=0, y=9, width=64, height=1, percentage=1.0, color=Colors.CYAN, outline=False)

    clock_widget = DateTimeWidget(x=12, y=20, font=resources.medium_01, color=Colors.WHITE, format="%H:%M")
    
    seconds_widget = DateTimeWidget(x=26, y=30, font=resources.small_font, color=Color(150, 150, 150), format=":%S")

    # Static visual bars
    left_bar = BarWidget(x=2, y=15, width=3, height=40, percentage=0.75, color=Colors.MAGENTA, outline=True, outline_color=Color(50, 50, 50))

    right_bar = BarWidget(x=59, y=15, width=3, height=40, percentage=1.0, color=Colors.GREEN, outline=True, outline_color=Color(50, 50, 50))

    footer_text = TextWidget(text="NO DATA", x=18, y=56, font=resources.small_font, color=Colors.RED)

    widgets = [header_label, header_line, clock_widget, seconds_widget, left_bar, right_bar, footer_text]

    # --- DASHBOARD CREATION ---
    return Dashboard(
        background_color=bg_color,
        widgets=widgets
    )