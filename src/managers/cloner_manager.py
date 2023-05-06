# Handles management related to data cloners.

# imports, python
import inspect

# imports, third-party
from pathlib import Path


class ClonerManager:
    def __init__(self, config: dict):
        self._cloners_active = False

        # Assign args to class
        self._config = config

        # Init non-arg values
        self._cloners = []

        # Search local imports for enabled cloners
        # Initialize the enabled cloners
        enabled_cloners = self.config['enabled_cloners']

        # Collect imported objects for iteration
        content_root = config['paths']['content_root']
        data_cloners = collect_cloners(content_root=content_root)

        for cloner_name, cloner_cls in data_cloners:
            if not cloner_cls:
                continue  # Skip None

            if not inspect.isclass(cloner_cls):
                continue  # Skip non-class objects

            if not hasattr(cloner_cls, "_NAME"):
                continue  # Skip objects without name attribute

            if not cloner_cls._NAME:
                continue  # Skip objects without a name

            if cloner_cls._NAME not in enabled_cloners:
                continue  # Skip names that are listed in config as enabled

            # Initialize the cloner and store it to the manager
            self.cloners.append(cloner_cls)

    @property
    def cloners(self) -> list:
        return self._cloners

    @cloners.setter
    def cloners(self, value: list):
        self._cloners = value

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
        # Run the initialized cloners
        # TODO dispatch asynchronously when >1 cloner
        for cloner in self.cloners:
            cloner.run()


def collect_cloners(content_root: Path) -> list:
    """Browse imported objects, inspect them, and return a list of the
        ones that meet the requirements for a cloner.

    :return: a list of cloner objects
    """
    # Extract all classes from cloners
    # 1. Collect python modules that are not __init__
    # 2. Per module, inspect and identify classes
    # 3. Per found class, eliminate those not pre-listed as cloners
    # 4. Attempt instantiation of each cloner class
    path_to_cloners = Path(content_root, 'src', 'cloners')
    cloner_objects = inspect.getmembers(path_to_cloners)
    classes = []
    for name, obj in cloner_objects:
        if inspect.isclass(obj):
            classes.append(obj)
        pass

    return []
