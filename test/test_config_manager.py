# Test objects in config manager module

# imports, python
import os

# imports, third-party
import pytest

# imports, project
from src.managers.config_manager import ConfigManager
from src.managers.config_manager import add_dotenv_to_config
from test.mock import mock_config


def test_config_manager():
    cm = ConfigManager()
    assert cm, f"Class failed to initialize"

    # Test function return
    config = cm.read_config()
    assert config, f"Class function {cm.read_config.__name__} returned nothing."
    assert isinstance(config, dict), "Returned config is not dict."

    # Test for expected keys
    parent_key = 'paths'
    assert parent_key in config, f"Missing dict key : {parent_key}"
    # Test for expected keys in 'path' sub-dict
    child_key = 'content_root'
    assert child_key in config[parent_key], f"Missing dict child_key : {child_key}"

    # Test raises exception with bad path
    with pytest.raises(Exception):
        cm.read_config(path_to_config='/a/b/c/d/e')


def test_add_dotenv_to_config(mconfig=mock_config):
    # Test function return

    dotenv = add_dotenv_to_config(config=mconfig)
    assert dotenv, f"Function \'{add_dotenv_to_config.__name__}\' returned " \
                   f"nothing."
    assert isinstance(dotenv, dict), "Returned config is not dict."

    # Test raises exception with bad filename
    with pytest.raises(Exception):
        add_dotenv_to_config(dotenv_filename='abcdefghijklmnopqrstuvwxyz',
                             config=mconfig)
