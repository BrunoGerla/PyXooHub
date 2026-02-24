import json
import time
from pathlib import Path
from dataclasses import dataclass

from providers.mouse_battery.base import MouseProvider
from utils.logger import get_logger

logger = get_logger("RazerSynapseProvider")

@dataclass
class MouseData:
    battery_percentage: float = 0.0
    is_charging: bool = False

class RazerSynapseProvider(MouseProvider):
    """Provides Razer mouse battery and charging data by polling local Synapse log files."""
    
    def __init__(self, update_interval_seconds: int = 5) -> None: 
        self._log_dir: Path = Path.home() / "AppData" / "Local" / "Razer" / "RazerAppEngine" / "User Data" / "Logs"
        self._update_interval: int = update_interval_seconds     
        
        self._last_check_time: float = 0.0
        self._last_modified_time: float = 0.0
        self._cached_file: Path | None = None
        
        self._data: MouseData = MouseData()

        logger.debug(f"Razer Synapse Log Directory: {self._log_dir}")
        self._poll_logs() # Initial fetch

    def update(self, dt: float) -> None:
        """Called every frame to process file timers."""
        current_time = time.time()
        if current_time - self._last_check_time > self._update_interval:
            self._poll_logs()

    @property
    def battery_percentage(self) -> float:
        """Pure getter. Returns the cached battery percentage."""
        return self._data.battery_percentage
    
    @property
    def is_charging(self) -> bool:
        """Pure getter. Returns the cached charging status."""
        return self._data.is_charging

    def _poll_logs(self) -> None:
        """Checks the cached file for updates, or scans for a new file if the current one is idle."""
        self._last_check_time = time.time()

        if not self._log_dir.exists():
            return

        if not self._cached_file or not self._cached_file.exists():
            self._cached_file = self._get_newest_file_in_dir()
            if not self._cached_file:
                return
            
            self._last_modified_time = self._cached_file.stat().st_mtime
            self._parse_file(self._cached_file)
            return

        current_mtime = self._cached_file.stat().st_mtime
        
        if current_mtime > self._last_modified_time:
            logger.debug(f"Log modified. Reading {self._cached_file.name}")
            self._parse_file(self._cached_file)
            self._last_modified_time = current_mtime
            
        else:
            latest_file = self._get_newest_file_in_dir()
            
            if latest_file and latest_file != self._cached_file:
                logger.info(f"New log file detected: {latest_file.name}")
                self._cached_file = latest_file
                self._last_modified_time = latest_file.stat().st_mtime
                self._parse_file(self._cached_file)

    def _get_newest_file_in_dir(self) -> Path | None:
        """Helper to safely find the newest log file in the directory."""
        files = list(self._log_dir.glob("systray_systray*.log"))
        if not files:
            return None
        return max(files, key=lambda f: f.stat().st_mtime)

    def _parse_file(self, filename: Path) -> None:
        """Reads the log backwards to extract and cache the latest device JSON payload."""
        try:
            with filename.open("r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line in reversed(lines):
                if "info: Device" in line:
                    parts = line.split("info: Device", 1)
                    if len(parts) > 1:
                        try:
                            json_data = json.loads(parts[1].strip())
                            
                            for device in json_data:
                                if "powerStatus" in device:
                                    level = device["powerStatus"].get("level")
                                    is_charging = device["powerStatus"].get("isCharging", False)
                                    
                                    if level is not None:
                                        new_battery_pct = float(level) / 100.0
                                        
                                        # Only log if the data actually changed
                                        if new_battery_pct != self._data.battery_percentage or is_charging != self._data.is_charging:
                                            self._data.battery_percentage = new_battery_pct
                                            self._data.is_charging = is_charging
                                            logger.info(f"Razer Mouse Updated -> Battery: {new_battery_pct * 100:.0f}% | Charging: {is_charging}")
                                            
                                        return 

                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Failed to parse log file: {e}")

if __name__ == "__main__":
    provider = RazerSynapseProvider()
    
    provider.update(0.1) 
    
    print(f"Battery: {provider.battery_percentage * 100}%")
    print(f"Charging: {provider.is_charging}")