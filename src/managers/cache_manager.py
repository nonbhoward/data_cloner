# Manage the cache in the form of json metadata

# imports, python
from pathlib import Path

# imports, project
from src.managers.config_manager import ConfigManager


class CacheManager:
    def __init__(self, config_manager: ConfigManager):
        self._config_manager = config_manager

    def read(self) -> dict:
        pass

    def write(self, cache: dict):
        pass
