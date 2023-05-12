# Example cloner with minimal required properties

"""Bare minimum example for a new cloner

In order to add a new cloner :

    1. Create a new cloner class
    2. Set cls._ACTIVE attribute to True
    3. Add the class name to config.yaml attribute 'enabled_cloners'

Now the cloner manager should find it
"""

# imports, project
from src.managers.config_manager import ConfigManager


class ExampleCloner:
    _ACTIVE = True

    def __init__(self, config_manager: ConfigManager):
        self._config_manager = config_manager

    def authenticate(self):
        """
        This will authenticate with whatever API and be different for each
          cloner.
        """
        pass
