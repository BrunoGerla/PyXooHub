from datetime import datetime
from widgets.text import TextWidget

class DateTimeWidget(TextWidget):
    """
    A specialized TextWidget that displays the current date or time, formatted throught the format argument.
    """
    def __init__(self, x: int, y: int, format: str = "%H:%M:%S", **kwargs):
        def time_provider():
            return datetime.now().strftime(format)
        
        super().__init__(
            x=x,
            y=y,
            data_source=time_provider,
            **kwargs
        )