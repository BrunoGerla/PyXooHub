import time
import requests
from dataclasses import dataclass
from utils.geo import LocationProvider
from utils.weather_codes import get_weather_description
from utils.logger import get_logger, configure_logging
from utils.profiler import time_it

logger = get_logger("WeatherProvider")


@dataclass
class WeatherData:
    temperature: float = 0.0
    weather_code: int = 0
    is_day: bool = True
    weather_description: str = "UNKNOWN"


class WeatherProvider:
    """Provides local weather data by polling the Open-Meteo API."""

    def __init__(self, location_provider: LocationProvider, update_interval_min: int = 15) -> None:
        self._location: LocationProvider = location_provider

        self._update_interval: int = update_interval_min * 60

        self._last_fetch_time: float = 0.0
        self._data: WeatherData = WeatherData()

        self._refresh()

    def update(self, dt: float) -> bool:
        """Called every frame by the dashboard to handle background polling."""
        return self._check_timer()

    @property
    def temperature(self) -> float:
        return self._data.temperature

    @property
    def weather_code(self) -> int:
        return self._data.weather_code

    @property
    def is_day(self) -> bool:
        return self._data.is_day

    @property
    def weather_description(self) -> str:
        return self._data.weather_description

    def _check_timer(self) -> bool:
        """Prevents API spam. Only fetches if data is stale."""
        current_time = time.time()

        logger.debug(f"Checking weather timer. Fetch: {current_time-self._last_fetch_time:.1f}s/{self._update_interval}s")

        if current_time - self._last_fetch_time > self._update_interval:
            return self._refresh()

        return False

    @time_it(threshold_ms=5.0)
    def _refresh(self) -> bool:
        """Performs the actual HTTP request to Open-Meteo."""
        logger.info("Refreshing Weather Information.")
        loc = self._location

        if loc.lat == 0.0 and loc.lon == 0.0:
            self._location.refresh()
            if self._location.lat == 0.0:
                logger.warning("Missing location data. Skipping weather fetch.")
                return False

        try:
            logger.debug(f"Fetching weather for {loc.city}...")
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": loc.lat,
                "longitude": loc.lon,
                "current_weather": "true"
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            json_data = resp.json().get("current_weather", {})

            changed = False
            if isinstance(json_data, dict):
                new_data = WeatherData(
                    temperature=json_data.get("temperature", 0.0),
                    weather_code=json_data.get("weathercode", 0),
                    is_day=bool(json_data.get("is_day", 1)),
                    weather_description=get_weather_description(json_data.get("weathercode", "UNKNOWN"))
                )
                changed = new_data != self._data
                self._data = new_data

                logger.info(f"Weather Updated: {self._data.temperature} C | {self._data.weather_description}")

            self._last_fetch_time = time.time()
            return changed
        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return False


if __name__ == "__main__":
    configure_logging()

    location = LocationProvider()
    weather = WeatherProvider(location)

    # Simulate main loop
    weather.update(0.1)

    # Now these are accessed without parentheses!
    print(f"Temperature: {weather.temperature}")
    print(f"Description: {weather.weather_description}")
