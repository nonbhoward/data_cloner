# Handles management related to data cloners.

# imports, project
from src.cloners.google_drive_cloner import GoogleDriveDataCloner


class ClonerManager:
    def __init__(self, config: dict):
        # Assign args to class
        self._config = config

        # Init non-arg values
        self._cloners = []
        self._cloners_active = False

    @property
    def cloners_active(self) -> bool:
        return self._cloners_active

    @cloners_active.setter
    def cloners_active(self, value: bool) -> None:
        if not isinstance(value, bool):
            print(f'warning, non-bool value {value} passed to '
                  f'{self.__class__.__name__} attribute')
            return
        self._cloners_active = value

    @property
    def config(self) -> dict:
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    def run(self):
        # Collect the enabled classes
        enabled_cloners = self.config['enabled_cloners']
        # Initialize the enabled classes
        # Run the successfully initialized cloners
        pass
