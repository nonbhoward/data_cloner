# Manage the cache in the form of json metadata

# imports, project
from src.managers.config_manager import ConfigManager


class MetadataManager:
    def __init__(self, config_manager: ConfigManager):
        print(f'Initializing {self.__class__.__name__}')
        self._config_manager = config_manager

    def read(self) -> dict:
        pass

    def write(self, cache: dict):
        pass
