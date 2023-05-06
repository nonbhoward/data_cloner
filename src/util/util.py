# General utilities with broad use

# imports, python
from os import getcwd
from pathlib import Path


# TODO should this be relocated?
default_project_name = 'data_cloner'


def find_content_root(project_name=default_project_name) -> Path:
    """Locate the project root, aka the content root, without relying on
        relative directories. The downside of this is that it relies on
        a defined project name to be found in the path.

    :param project_name: override default project name.
    :return: the path to the content root."""

    # Determine project name
    project_name = project_name if project_name else default_project_name

    # Use metadata variable 'project_name' to find content root
    path_elements = getcwd().split('/')
    assert project_name in path_elements, f"Project name {project_name} not " \
                                          f"found in path"
    content_root_index = None
    for path_element_index, path_element in enumerate(path_elements):
        if project_name in path_element:
            content_root_index = path_element_index + 1
            break  # content root found, stop

    # Build path to content root
    path_to_content_root_elements = path_elements[:content_root_index]
    path_to_content_root = Path('/', * path_to_content_root_elements)
    return path_to_content_root
