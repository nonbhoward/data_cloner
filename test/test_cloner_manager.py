# Test objects in cloner manager module

# imports, project
from src.managers.cloner_manager import collect_cloners
from src.util.util import find_content_root
from test.mock import mock_config


def test_cloner_manager(m_config=mock_config):
    # TODO implement a test
    # cm = ClonerManager(config=m_config)
    pass


def test_collect_cloners(m_config=mock_config):
    content_root = find_content_root()

    enabled_cloners = m_config['enabled_cloners']
    cloners = collect_cloners(content_root=content_root,
                              enabled_cloners=enabled_cloners)

    # Test that a cloner is found
    message = 'No cloners found!'
    assert cloners, message
