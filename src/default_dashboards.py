from engine.dashboard import Dashboard
from engine.color import Colors, Color
import resources

# Widgets
from widgets.container import VerticalContainer, HorizontalContainer
from widgets.text import TextWidget
from widgets.datetime import DateTimeWidget
from widgets.bar import BarWidget
from widgets.spacer import Spacer
from widgets.gap import Gap

from utils.geo import LocationProvider
from providers.weather.weather_provider import WeatherProvider

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

class TutorialDashboard(Dashboard):
    """
    A minimalistic dashboard showcasing the layout engine.
    Features a styled header, side-by-side data widgets, and a footer bar.
    """
    
    # --- THEME / PALETTE ---
    BG_COLOR       = Color(15, 15, 20)  # Dark grey/blue
    HEADER_BG      = Color(40, 40, 55)  # Distinct, lighter background for the header
    HEADER_COLOR   = Colors.CYAN        # Cyan looks great against dark blue
    CLOCK_COLOR    = Colors.WHITE
    TEMP_COLOR     = Colors.YELLOW
    FOOTER_TEXT    = Color(100, 100, 100) # Dim grey for footer text

    def __init__(self):
        # Apply background color from palette
        super().__init__(background_color=self.BG_COLOR)

        # --- 1. INITIALIZE PROVIDERS ---
        self.location = LocationProvider()
        self.weather = WeatherProvider(self.location)

        # --- 2. CREATE WIDGETS ---
        # Header & Main Data
        self.header_label = TextWidget(text="PYXOOHUB", color=self.HEADER_COLOR, name="HeaderText")
        self.clock = DateTimeWidget(format="%H:%M", font=resources.medium_01, color=self.CLOCK_COLOR, name="Clock")
        self.temp_label = TextWidget(data_source=lambda: f"{self.weather.temperature:.1f}°C", color=self.TEMP_COLOR, name="Temp")
        
        # Footer Widgets (Showcasing the BarWidget!)
        self.footer_label = TextWidget(text="SYS", color=self.FOOTER_TEXT, name="FooterLabel")
        self.sys_bar = BarWidget(
            width=39, 
            height=5, 
            percentage=0.65,      # Static for the tutorial, but could be tied to a data_source!
            color=Colors.GREEN, 
            outline=True, 
            outline_color=Color(50, 50, 50),
            name="SysBar"
        )

        # --- 3. ASSEMBLE LAYOUT ---
        
        # Top Header Bar
        header_bar = HorizontalContainer(
            width=64, height=11, color=self.HEADER_BG, align="center",
            children=[Spacer(), self.header_label, Spacer()], name="HeaderBar"
        )

        # Middle Data Row
        data_row = HorizontalContainer(
            width=64, align="center",
            children=[Spacer(), self.clock, Spacer(), self.temp_label, Spacer()], name="DataRow"
        )

        # Bottom Footer Row
        footer_row = HorizontalContainer(
            width=64, height=9, align="center", padding=2, spacing=4, autosize=False,
            children=[Spacer(), self.footer_label, self.sys_bar, Spacer()], name="FooterRow"
        )

        # Main Vertical Stack
        main_layout = VerticalContainer(
            width=64, autosize=False, spacing=0,
            children=[
                header_bar,
                Gap(10),           # Hardcoded distance from header to data
                data_row,
                Spacer(),          # <--- Pushes the footer_row firmly to the bottom!
                footer_row
            ], name="MainLayout"
        )

        # --- 4. ADD TO DASHBOARD ---
        self.add_widget(main_layout)

    def update(self, dt: float):
        super().update(dt)
        self.weather.update(dt)

DEFAULT_DASHBOARDS = {
    "CyberPunk": build_cyberpunk_dashboard,
    "Tutorial Dashboard": TutorialDashboard
}