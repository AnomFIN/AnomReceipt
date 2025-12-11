"""
Configuration management for the receipt printing application.
"""
import json
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


DEFAULT_SETTINGS = {
    "printer": {
        "connection_type": "usb",  # "usb" or "network"
        "device_path": None,
        "ip_address": None,
        "port": 9100
    },
    "defaults": {
        "company": "Harjun Raskaskone Oy",
        "language": "FI",
        "currency": "EUR"
    },
    "ui": {
        "window_width": 1200,
        "window_height": 800
    },
    "receipt": {
        "width": 42  # characters per line
    }
}


class Settings:
    """Application settings manager."""
    
    def __init__(self, config_file: str = "config/settings.json"):
        """
        Initialize settings.
        
        Args:
            config_file: Path to settings JSON file
        """
        self.config_file = config_file
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()
    
    def load(self):
        """Load settings from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    self._deep_update(self.settings, loaded)
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
    
    def save(self):
        """Save settings to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def _deep_update(self, base: dict, update: dict):
        """Recursively update nested dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default=None):
        """Get a setting value using dot notation."""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def set(self, key: str, value):
        """Set a setting value using dot notation."""
        keys = key.split('.')
        target = self.settings
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
    
    def get_printer_config(self) -> dict:
        """Get printer configuration."""
        return self.settings.get("printer", {})
    
    def set_printer_config(self, config: dict):
        """Set printer configuration."""
        self.settings["printer"] = config
        self.save()
    
    def get_default_company(self) -> Optional[str]:
        """Get default company name."""
        return self.get("defaults.company")
    
    def set_default_company(self, company: str):
        """Set default company name."""
        self.set("defaults.company", company)
        self.save()
    
    def get_default_language(self) -> str:
        """Get default language."""
        return self.get("defaults.language", "FI")
    
    def set_default_language(self, language: str):
        """Set default language."""
        self.set("defaults.language", language)
        self.save()

    # Receipt settings helpers
    def get_receipt_width(self) -> int:
        return int(self.get("receipt.width", 42))

    def set_receipt_width(self, width: int):
        self.set("receipt.width", int(width))
        self.save()
