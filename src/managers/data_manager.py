# A class to handle actions against local files

# imports, project
from src.managers.config_manager import ConfigManager


class FileManager:
    def __init__(self, config_manager: ConfigManager):
        self._open_files = dict

    def read(self) -> dict:
        pass

    def write(self, content):
        pass
