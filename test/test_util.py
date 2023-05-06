# imports, python
import os

# imports, third-party
import pytest

# imports, project
from src.util.util import find_content_root


def test_find_content_root():
    path_to_content_root = find_content_root()
    assert os.path.exists(path_to_content_root), \
        f"Path does not exist : {path_to_content_root}"

    with pytest.raises(Exception):
        find_content_root(project_name='abcdefghijklmnopqrstuvwxyz')


