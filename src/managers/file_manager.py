# A class to handle actions against local files

# imports, python
from pathlib import Path

# imports, project
from src.managers.config_manager import ConfigManager


class FileManager:
    def __init__(self,
                 config_manager: ConfigManager,
                 path_to_manage: Path):
        self._path_to_manage = path_to_manage

    @property
    def path_to_manage(self) -> Path:
        return self._path_to_manage

    @path_to_manage.setter
    def path_to_manage(self, value: Path):
        self._path_to_manage = value
