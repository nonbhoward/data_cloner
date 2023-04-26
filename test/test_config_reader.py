# imports, python
import os

# imports, third-party
import pytest

# imports, project
from src.config_reader.config_reader import *


def test_find_content_root():
    path_to_content_root = find_content_root()
    assert os.path.exists(path_to_content_root), \
        f"Path does not exist : {path_to_content_root}"

    with pytest.raises(Exception):
        find_content_root(project_name='abcdefghijklmnopqrstuvwxyz')


def test_read_config():
    # Test function return
    config = read_config()
    assert config, f"Function {read_config.__name__} returned nothing."
    assert isinstance(config, dict), "Returned config is not dict."

    # Test for expected keys
    key = 'path'
    assert key in config, f"Missing key {key}"
    # Test for expected keys in 'path' sub-dict
    key = 'content_root'
    assert key in config['path'], f"Missing path key {key}"

    # Test raises exception with bad path
    with pytest.raises(Exception):
        read_config(path_to_config='/a/b/c/d/e')


def test_read_dotenv():
    # Test function return
    dotenv = read_dotenv()
    assert dotenv, f"Function {read_dotenv.__name__} returned nothing."
    assert isinstance(dotenv, dict), "Returned config is not dict."

    # Test raises exception with bad path
    with pytest.raises(Exception):
        read_dotenv(dotenv_filename='abcdefghijklmnopqrstuvwxyz')
