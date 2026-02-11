from __future__ import annotations
import colorsys
from utils.logger import get_logger

logger = get_logger("ColorEngine")

class Color:
    """
    Smart Color class. 
    Stores RGB and HSL internally.
    Can be used exactly like a tuple: r, g, b = my_color
    """
    __slots__ = ('r', 'g', 'b', '_h', '_s', '_v')

    def __init__(self, r: int, g: int, b: int) -> None:
        self.r = self._validate_channel(r)
        self.g = self._validate_channel(g)
        self.b = self._validate_channel(b)

        self._h, self._s, self._v = colorsys.rgb_to_hsv(
            self.r / 255.0, 
            self.g / 255.0, 
            self.b / 255.0
        )

    def _validate_channel(self, value: int) -> int:
        if not isinstance(value, int):
            raise TypeError(f"Color Channel Value must be of type Integer.")
        if not (0 <= value <= 255):
            raise ValueError(f"Color Channel Value must be between 0 and 255.")
        return value
    
    @staticmethod
    def _clamp_rgb(val: int) -> int:
        """Ensures math results fit into 0-255 before creating a Color"""
        return max(0, min(255, val))
    
    def __getitem__(self, index: int) -> int:
        """Allows driver to read [0], [1], [2] without knowing it's a Class"""
        return (self.r, self.g, self.b)[index]
    
    def __iter__(self):
        """Allows unpacking: r, g, b = color"""
        yield self.r
        yield self.g
        yield self.b

    def __len__(self):
        return 3

    def __eq__(self, other):
        """Allows: if my_color == Colors.RED"""
        if isinstance(other, (Color, tuple)):
            return len(self) == len(other) and self.r == other[0] and self.g == other[1] and self.b == other[2]
        return False
    
    def __repr__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b})"
    
    @staticmethod
    def parse(value: "ColorValue", default: Color | None= None) -> Color:
        if isinstance(value, Color):
            return value
        if isinstance(value, tuple) and len(value) == 3:
            if isinstance(value[0], int) and isinstance(value[1], int) and isinstance(value[2], int):
                return Color(*value)
            if isinstance(value[0], float) and isinstance(value[1], float) and isinstance(value[2], int):
                return Color.from_hsv(*value)
        if isinstance(value, str) and len(value.strip().lstrip("#")) == 6:
            return Color.from_hex(value)
        if isinstance(default, Color):
            logger.warning(f"Warning: Could not parse value ({value}) to valid Color Object. Returning Default {default}")
            return default
        else:
            logger.warning(f"Warning: Could not parse value ({value}) to valid Color Object.")
            raise ValueError(f"Invalid Color Format: {value}")
    
    @classmethod
    def from_hex(cls, hex_str: str) -> Color:
        """Creates a Color from a hex string like '#ff0000'"""
        hex_str = hex_str.strip().lstrip('#')

        if len(hex_str) != 6:
            raise ValueError(f"Invalid hex length: '{hex_str}'")
        
        return cls(*tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4)))
    
    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> Color:
        """
        Creates a color from Hue, Saturation, Value.
        h, s, v should be floats between 0.0 and 1.0
        """
        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        obj = cls.__new__(cls)
        obj.r = int(r * 255)
        obj.g = int(g * 255)
        obj.b = int(b * 255)

        obj._h, obj._s, obj._v = h, s, v
        return obj
    
    def __add__(self, other: Color | int) -> Color:
        """
        Allows: Color(10,0,0) + Color(0,10,0) -> Color(10,10,0)
        Allows: Color(10,0,0) + 50 -> Color(60, 50, 50) (Brighten)
        """
        if isinstance(other, int):
            return Color(self._clamp_rgb(self.r + other), self._clamp_rgb(self.g + other), self._clamp_rgb(self.b + other))
        elif isinstance(other, Color):
            return Color(self._clamp_rgb(self.r + other.r), self._clamp_rgb(self.g + other.g), self._clamp_rgb(self.b + other.b))
        else:
            return NotImplemented

    def __sub__(self, other: Color | int) -> Color:
        """
        Allows: Color(50,50,50) - 10 -> Color(40,40,40) (Darken)
        """
        if isinstance(other, int):
            return Color(self._clamp_rgb(self.r - other), self._clamp_rgb(self.g - other), self._clamp_rgb(self.b - other))
        if hasattr(other, 'r'):
            return Color(self._clamp_rgb(self.r - other.r), self._clamp_rgb(self.g - other.g), self._clamp_rgb(self.b - other.b))
        return NotImplemented
    
    def __mul__(self, factor: float) -> Color:
        """Scales the brightness of the color."""
        factor  = max(0.0, factor)

        return Color(
            self._clamp_rgb(int(self.r * factor)),
            self._clamp_rgb(int(self.g * factor)),
            self._clamp_rgb(int(self.b * factor))
        )
    
    def shift_hue(self, amount: float) -> Color:
        """
        Returns a new Color with the hue shifted by amount (0.0 - 1.0).
        """
        new_h = (self._h + amount) % 1.0
        return Color.from_hsv(new_h, self._s, self._v)
    
    def mix(self, other: Color, factor: float) -> Color:
        factor = max(0.0, min(1.0, factor))
        return Color(
            self._clamp_rgb(int(self.r + (other.r - self.r) * factor)),
            self._clamp_rgb(int(self.g + (other.g - self.g) * factor)),
            self._clamp_rgb(int(self.b + (other.b - self.b) * factor))
        )
    
class Colors:
    # Basic
    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    
    # Primaries
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)
    
    # Secondary
    YELLOW = Color(255, 255, 0)
    CYAN = Color(0, 255, 255)
    MAGENTA = Color(255, 0, 255)

    # Other
    AMBER = (255, 160, 0)
    
    # UI Specific
    WARNING = AMBER
    DANGER = Color(220, 20, 60)
    SUCCESS = Color(50, 205, 50)

ColorValue = Color | tuple[int, int, int] | str