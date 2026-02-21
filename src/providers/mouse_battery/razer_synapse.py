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
    def __init__(self, update_interval_seconds: int = 5, discovery_interval_seconds: int = 300) -> None: 
        self._log_dir: Path = Path.home() / "AppData" / "Local" / "Razer" / "RazerAppEngine" / "User Data" / "Logs"
        
        self._update_interval: int = update_interval_seconds     
        self._discovery_interval: int = discovery_interval_seconds 
        
        self._last_fetch_time: float = 0.0
        self._last_discovery_time: float = 0.0
        self._last_modified_time: float = 0.0
        self._cached_file: Path | None = None
        
        self._data: MouseData = MouseData()

        logger.debug(f"Razer Synapse Log Directory: {self._log_dir}")
        self._discover_latest_log() 

    def get_battery_percentage(self) -> float:
        """Returns the cached battery percentage, triggering a background update if needed."""
        self._check_timers()
        return self._data.battery_percentage
    
    def is_charging(self) -> bool:
        """Returns the cached charging status, triggering a background update if needed."""
        self._check_timers()
        return self._data.is_charging

    def _check_timers(self) -> None:
        """Triggers fast file reads or slow directory scans based on elapsed time."""
        current_time = time.time()

        if current_time - self._last_discovery_time > self._discovery_interval:
            self._discover_latest_log()

        if current_time - self._last_fetch_time > self._update_interval:
            self._poll_active_log()

    def _poll_active_log(self) -> None:
        """Fast refresh: parses the cached log file only if its modified time has changed, with stale-cache fallback."""
        self._last_fetch_time = time.time()

        if not self._cached_file or not self._cached_file.exists():
            return 

        logger.debug(f"Checking cached log for changes: {self._cached_file.name}")

        if self._has_file_changed():
            try:
                current_mtime = self._cached_file.stat().st_mtime
                if self._last_modified_time > 0:
                    time_between_writes = current_mtime - self._last_modified_time
                    logger.debug(f"Synapse Log Updated! Time since last write: {time_between_writes:.1f}s.")

                self._parse_file(self._cached_file)
                self._last_modified_time = current_mtime
            except Exception as e:
                logger.error(f"Error reading cached log file: {e}")
                self._cached_file = None 
        else:
            try:
                current_mtime = self._cached_file.stat().st_mtime
                time_since_last_write = time.time() - current_mtime
                time_since_last_discovery = time.time() - self._last_discovery_time
                
                if time_since_last_write > 120 and time_since_last_discovery > 60:
                    logger.warning("Active log appears stale. Forcing early discovery scan...")
                    self._discover_latest_log()
            except OSError:
                pass 

    def _has_file_changed(self) -> bool:
        """Returns True if the cached log file's modified time is newer than our last read."""
        if not self._cached_file:
            return False
        
        try:
            current_mtime = self._cached_file.stat().st_mtime
            return current_mtime > self._last_modified_time
        except OSError:
            logger.warning(f"Could not read stats for {self._cached_file.name}. It may have been deleted.")
            return False

    def _discover_latest_log(self) -> None:
        """Slow refresh: Scans the Synapse directory to find the newest log file (handles log rotation)."""
        self._last_discovery_time = time.time() 
        
        logger.debug("Discovering: Scanning directory for newest log.")
        if not self._log_dir.exists():
            logger.warning(f"Directory for RazerSynapse Logs not found: {self._log_dir}")
            return
        
        log_format = "systray_systray*.log"
        files = list(self._log_dir.glob(log_format))

        if not files:
            logger.warning(f"Synapse Log Directory does not contain format: {log_format}")
            return
        
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        
        if latest_file != self._cached_file:
            logger.info(f"New active log file assigned: {latest_file.name}")
            self._cached_file = latest_file
            self._last_modified_time = 0.0 
        else:
            logger.debug("Directory scan complete. Active log is still the newest file.")

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
    print(f"Battery: {provider.get_battery_percentage() * 100}%")
    print(f"Charging: {provider.is_charging()}")