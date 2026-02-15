from engine.dashboard import Dashboard
from engine.color import Colors, Color
import resources

# Widgets
from widgets.container import VerticalContainer, HorizontalContainer
from widgets.text import TextWidget
from widgets.datetime import DateTimeWidget
from widgets.bar import BarWidget
from widgets.spacer import Spacer

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

class LayoutTestDashboard(Dashboard):
    def __init__(self):
        super().__init__()

        # --- 1. CREATE WIDGETS (The "Ingredients") ---
        # We define them as 'self.' so we can update their text later!
        
        # Top Label
        self.header_label = TextWidget(text="SYSTEM", color=Colors.WHITE)
        
        # The 3 Status Widgets
        self.cpu_label = TextWidget(text="CPU: 12%", color=Colors.GREEN)
        self.ram_label = TextWidget(text="RAM: 45%", color=Colors.YELLOW)
        self.net_label = TextWidget(text="NET: UP", color=Colors.CYAN)

        # Footer items
        self.footer_left = TextWidget(text="A", color=Colors.RED)
        self.footer_right = TextWidget(text="B", color=Colors.RED)

        # Spacers (We can make them on the fly or define them here)
        main_spacer = Spacer()
        footer_spacer = Spacer()


        # --- 2. ASSEMBLE CONTAINERS (The "Recipe") ---

        # The Header Row
        header_container = HorizontalContainer(
            height=10,
            width=64,
            color=Colors.BLUE,
            align="center", # Vertically center the text
            children=[self.header_label]
        )

        # The Footer Row (Left text, Spacer, Right text)
        footer_container = HorizontalContainer(
            height=12,
            width=64,
            color=Color(200, 200, 200),
            align="center",
            children=[
                self.footer_left,
                footer_spacer, # Pushes B to the right
                self.footer_right
            ]
        )

        # The Main Vertical Stack
        main_layout = VerticalContainer(
            x=0, y=0,
            width=64,
            # fixed_height=None (default) -> Fills screen
            spacing=1,
            children=[
                header_container,
                self.cpu_label,
                self.ram_label,
                self.net_label,
                main_spacer,      # <--- The magic spacer pushing footer down
                footer_container
            ]
        )

        # --- 3. ADD TO DASHBOARD ---
        self.add_widget(main_layout)

    def update(self, dt: float):
        super().update(dt)

DEFAULT_DASHBOARDS = {
    "Layout Test": LayoutTestDashboard,
    "CyberPunk": build_cyberpunk_dashboard
}