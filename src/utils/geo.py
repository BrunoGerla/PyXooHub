import requests
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger("GeoUtil")

@dataclass
class LocationData:
    country: str
    region: str
    city: str
    country_code: str
    region_code: str
    lat: float
    lon: float
    timezone: str

class LocationProvider:
    def __init__(self) -> None:
        self._data: LocationData | None = None
        self.refresh()
        
    @property
    def country(self) -> str:
        return self._data.country if self._data else "Unknown"
    
    @property
    def region(self) -> str:
        return self._data.region if self._data else "Unknown"
    
    @property
    def city(self) -> str:
        return self._data.city if self._data else "Unknown"
    
    @property
    def country_code(self) -> str:
        return self._data.country_code if self._data else "Unknown"
    
    @property
    def region_code(self) -> str:
        return self._data.region_code if self._data else "Unknown"
    
    @property
    def lat(self) -> float:
        return self._data.lat if self._data else 0.0
    
    @property
    def lon(self) -> float:
        return self._data.lon if self._data else 0.0
    
    @property
    def coordinates(self) -> tuple[float, float]:
        return (self._data.lat, self._data.lon) if self._data else (0.0, 0.0)
    
    @property
    def timezone(self) -> str:
        return self._data.timezone if self._data else "Unknown"
    
    def refresh(self):
        try:
            logger.info("Auto-detecting location via IP...")
            resp = requests.get("http://ip-api.com/json/", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            
            if isinstance(data, dict) and data.get("status") == "success":
                self._data = LocationData(
                    country=data.get("country", "Not Found"),
                    region=data.get("regionName", "Not Found"),
                    city=data.get("city", "Not Found"),
                    country_code=data.get("countryCode", "Not Found"),
                    region_code=data.get("region", "Not Found"),
                    lat=data.get("lat", "Not Found"),
                    lon=data.get("lon", "Not Found"),
                    timezone=data.get("timezone", "Not Found")
                )
                logger.info(f"Location found: {self.city} ({self.lat}, {self.lon})")
            elif isinstance(data, dict):
                logger.error(f"Incorrect API response: {data}")
            else:
                logger.error(f"Incorrect API format: {data}")
                
        except Exception as e:
            logger.error(f"Failed to fetch location: {e}")

if __name__ == "__main__":
    provider = LocationProvider()

    print(provider._data)
