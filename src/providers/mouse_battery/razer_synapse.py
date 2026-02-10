import json
from pathlib import Path

from providers.mouse_battery.base import MouseProvider
from utils.logger import get_logger

logger = get_logger("RazerSynapseProvider")

class RazerSynapseProvider(MouseProvider):
    def __init__(self) -> None:
        self.log_dir = Path.home() / "AppData" / "Local" / "Razer" / "RazerAppEngine" / "User Data" / "Logs"
        self.last_val = 0.0

    def get_battery_percentage(self) -> float:
        try:
            log_file = self._get_latest_log_file()
            if not log_file:
                return self.last_val
            
            latest_json = self._get_latest_device_json(log_file)

            if latest_json:
                for device in latest_json:
                    if "powerStatus" in device:
                        level = device["powerStatus"].get("level")
                        if level is not None:
                            self.last_val = float(level) / 100.0
                            return self.last_val
            
            return self.last_val
        
        except Exception as e:
            logger.error(f"Error reading Razer logs: {e}")
            return self.last_val

    def _get_latest_log_file(self) -> Path | None:
        if not self.log_dir.exists():
            logger.warning(f"Directory for RazerSynapse Logs not found: {self.log_dir}")
            return None
        
        log_format = "systray_systray*.log"
        files = list(self.log_dir.glob(log_format))

        if not files:
            logger.warning(f"Synapse Log Directory ({self.log_dir}) does not contain any files that follow the right format ({log_format}).")
            return None
        
        logger.debug(f"Files found: {files}")

        return max(files, key=lambda f: f.stat().st_mtime)
    
    def _get_latest_device_json(self, filename: Path | None):
        """Scans the file backwards to find the last valid Device JSON line."""
        if not filename:
            return
        
        try:
            with filename.open("r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line in reversed(lines):
                if "info: Device" in line:
                    parts = line.split("info: Device", 1)
                    if len(parts) > 1:
                        json_str = parts[1].strip()
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            continue
            return None
        except Exception:
            return None


if __name__ == "__main__":
    provider = RazerSynapseProvider()

    print(provider.get_battery_percentage())