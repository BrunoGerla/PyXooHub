import time
import requests
from dataclasses import dataclass
from utils.geo import LocationProvider
from utils.weather_codes import get_weather_description
from utils.logger import get_logger, configure_logging

logger = get_logger("WeatherProvider")

@dataclass
class WeatherData:
    temperature: float = 0.0
    weather_code: int = 0
    is_day: bool = True
    weather_description: str = "UNKNOWN"

class WeatherProvider:
    def __init__(self, location_provider: LocationProvider, update_interval_min: int = 15) -> None:
        self.location = location_provider
        self.update_interval = update_interval_min * 60
        self.last_fetch_time = 0

        self.data: WeatherData = WeatherData()
        self._refresh()

    def temperature(self) -> float:
        self._check_refresh()
        return self.data.temperature
    
    def weather_code(self) -> int:
        self._check_refresh()
        return self.data.weather_code
    
    def is_day(self) -> bool:
        self._check_refresh()
        return self.data.is_day
    
    def weather_description(self) -> str:
        self._check_refresh()
        return self.data.weather_description

    def _check_refresh(self):
        """Prevents API spam. Only fetches if data is stale."""
        if time.time() - self.last_fetch_time > self.update_interval:
            self._refresh()

    def _refresh(self):
        loc = self.location

        if loc.lat == 0.0 and loc.lon == 0.0:
            self.location.refresh()
            if self.location.lat == 0.0:
                logger.warning("Missing location data. Skipping weather fetch.")
                return
            
        try:
            logger.info(f"Fetching weather for {loc.city}...")
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": loc.lat,
                "longitude": loc.lon,
                "current_weather": "true"
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            json_data = resp.json().get("current_weather", {})

            if isinstance(json_data, dict):
                self.data = WeatherData(
                    temperature=json_data.get("temperature", 0.0),
                    weather_code=json_data.get("weathercode", 0),
                    is_day=bool(json_data.get("is_day", 1)),
                    weather_description=get_weather_description(json_data.get("weathercode", "UNKNOWN"))
                )
                
                logger.info(f"Weather Updated: {self.data.temperature}°C")

            self.last_fetch_time = time.time()
        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")

if __name__ == "__main__":
    configure_logging()

    location = LocationProvider()
    weather = WeatherProvider(location)

    weather.temperature()