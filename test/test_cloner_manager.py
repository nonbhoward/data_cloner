# Test objects found in the cloner manager module

# imports, python
from pathlib import Path
import os

# imports, project
from src.managers.cloner_manager import ClonerManager
from src.managers.cloner_manager import collect_cloners


def test_cloner_manager():
    cm = ClonerManager(config={})
    pass


def test_collect_cloners():
    content_root = Path(os.getcwd()).parent
    cloners = collect_cloners(content_root=content_root)
