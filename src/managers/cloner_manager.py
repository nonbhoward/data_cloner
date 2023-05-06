# Handles management related to data cloners.

# imports, python
import importlib.machinery
import inspect
import os

# imports, third-party
from pathlib import Path

# imports, project
from src.managers.config_manager import ConfigManager


class ClonerManager:
    def __init__(self, config_manager: ConfigManager):
        self._cloners_active = False

        # Assign args to class
        self._config_manager = config_manager

        # Init non-arg values
        self._cloners = []

        # Search local imports for enabled cloners
        # Initialize the enabled cloners
        enabled_cloners = self._config_manager.enabled_cloners

        # Collect imported objects for iteration
        content_root = self._config_manager.content_root
        data_cloners = collect_cloners(content_root=content_root,
                                       enabled_cloners=enabled_cloners)

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


def collect_cloners(content_root: Path,
                    enabled_cloners: list) -> list:
    """Browse imported objects, inspect them, and return a list of the
        ones that meet the requirements for a cloner.

    :return: a list of cloner objects
    """
    # 0. Declare cloners location
    path_to_cloners = Path(content_root, 'src', 'cloners')

    # 1. Collect python modules that are not __init__
    py_modules = []
    for root, _, files in os.walk(path_to_cloners):
        for file in files:
            if not file.endswith('.py'):
                continue  # Skip non-python files

            if '__init__' in file:
                continue  # Skip __init__

            py_modules.append(Path(root, file))

    # 2. Per module, inspect and identify classes
    found_classes = []
    for py_module in py_modules:
        name = py_module.name.split('.')[0]
        mpath = str(py_module)
        module = importlib.machinery.SourceFileLoader(
            fullname=name,
            path=mpath
        )
        loaded_module = module.load_module()
        py_members = inspect.getmembers(object=loaded_module)

        # 2a. Eliminate non-class members
        for py_member in py_members:
            py_member_name = py_member[0]
            py_member_val = py_member[1]
            if not inspect.isclass(py_member_val):
                continue
            found_classes.append(py_member)

    # 3. Per found class, eliminate those not pre-listed as cloners
    cloner_classes = []
    for found_class in found_classes:

        if not is_cloner(f_class=found_class,
                         e_cloners=enabled_cloners):
            continue  # Skip non-cloner classes

        cloner_classes.append(found_class)

    # 4. Return object containing each cloner class
    return cloner_classes


def is_cloner(f_class: tuple,
              e_cloners: list) -> bool:
    key, val = f_class[0], f_class[1]
    if key not in e_cloners:
        return False
    return True
