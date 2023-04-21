# imports, third-party
import pytest

# imports, project
from src.config_reader.config_reader import *


def test_read_config():
    # Test function return
    config = read_config()
    assert config, f"Function {read_config.__name__} returned nothing."
    assert isinstance(config, dict), "Returned config is not dict."
    del config


def test_read_dotenv():
    # Test function return
    dotenv = read_dotenv()
    assert dotenv, f"Function {read_dotenv.__name__} returned nothing."
    assert isinstance(dotenv, dict), "Returned config is not dict."
