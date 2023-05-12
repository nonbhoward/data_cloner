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
        print(f'Initializing {self.__class__.__name__}')
        self._cloners_active = False
        self._initialized_cloners = []

        # Assign args to class
        self._config_manager = config_manager

        # Init non-arg values
        self._cloners = []

        # Search local imports for enabled cloners
        # Initialize the enabled cloners
        # Collect imported objects for iteration
        content_root = self._config_manager.content_root
        data_cloners = collect_cloners(
            content_root=content_root,
            enabled_cloners=self._config_manager.enabled_cloners
        )

        for cloner_name, cloner_cls in data_cloners:
            if not cloner_cls:
                continue  # Skip None

            if not inspect.isclass(cloner_cls):
                continue  # Skip non-class objects

            if not hasattr(cloner_cls, "_ACTIVE"):
                continue  # Skip objects without this attribute

            if not cloner_cls._ACTIVE:
                continue  # Skip objects where this attribute is falsy

            if cloner_cls.__name__ not in self._config_manager.enabled_cloners:
                continue  # Skip names not listed in config as enabled

            # Store the uninitialized cloner to the manager
            self.cloners.append(cloner_cls)

    @property
    def cloners(self) -> list:
        return self._cloners

    @cloners.setter
    def cloners(self, value: list):
        self._cloners = value

    @property
    def cloners_to_run(self) -> bool:
        return True if self.cloners else False

    @property
    def config(self) -> dict:
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def initialized_cloners(self) -> list:
        return self._initialized_cloners

    @initialized_cloners.setter
    def initialized_cloners(self, value: list):
        self._initialized_cloners = value

    def run(self):
        """The primary action for this class"""
        # Initialized the collected cloners
        self.initialize_cloners()
        self.dispatch_cloners()
        self.wait_for_cloners()

    def initialize_cloners(self):
        """Initialize cloners collected by this class"""

        initialized_cloners = []
        for cloner in self.cloners:
            try:
                # Initialize each cloner
                initialized_cloners.append(
                    cloner(config_manager=self._config_manager)
                )
            except Exception as exc:
                # TODO specify exceptions regarding failed class initialization
                raise exc
        self.initialized_cloners = initialized_cloners

    def dispatch_cloners(self):
        """Run cloners collected by this class"""
        # TODO dispatch asynchronously when >1 cloner
        # TODO when a cloner returns, delete it from self.cloners
        for initialized_cloner in self.initialized_cloners:
            try:
                initialized_cloner.run()
            except Exception as exc:
                # TODO specify exceptions
                raise exc

    def wait_for_cloners(self):
        pass


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
                continue  # Skip non-class objects
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
