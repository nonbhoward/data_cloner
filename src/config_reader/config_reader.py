# imports, python
from os import getcwd
from os import getenv
from pathlib import Path

# imports, third-party
import yaml

# imports, project
from metadata import project_name


def read_config(path_to_config='') -> dict:
    """Read the configuration file.
    Get the path to the configuration file, load it, return it. Avoiding
      dependency on relative paths.

    :param path_to_config: override automatically finding config.
    :return: The config dictionary."""

    # Use project_name metadata to find content root
    path_elements = getcwd().split('/')
    # TODO move this test to pytest?
    assert project_name in path_elements, f"Project name {project_name} not " \
                                          f"found in path"
    content_root_index = None
    for path_element_index, path_element in enumerate(path_elements):
        if project_name in path_element:
            content_root_index = path_element_index
            break  # content root found, stop

    # Build path to content root
    path_to_content_root_elements = path_elements[:content_root_index + 1]
    path_to_content_root = Path('/', * path_to_content_root_elements)

    # Extend content root to locate configuration
    path_to_config = Path(path_to_config) if path_to_config \
        else Path(path_to_content_root, 'config', 'config.yaml')

    # Read the configuration
    with open(path_to_config, 'r') as cfg_r:
        yaml_cfg = yaml.safe_load(cfg_r)

    # Append dotenv to config dictionary and return
    yaml_cfg.update({
        'dotenv': read_dotenv()
    })
    return yaml_cfg


def read_dotenv(dotenv_filename='.env') -> dict:
    """Read information stored outside project.

    Format Example :
      project_name;key1=value1;key2=value2; ... ;keyN=valueN

    :param dotenv_filename: the filename containing the information.
    :return: dictionary containing the dotenv information for this project.
    """
    # Use project_name metadata to find content root
    path_to_home = Path(getenv('HOME'))
    path_to_dotenv = Path(path_to_home, dotenv_filename)

    with open(path_to_dotenv, 'r') as env_r:
        dotenv_lines = env_r.readlines()

    # Locate the dotenv line for this project
    project_dotenv_line = None
    for dotenv_line in dotenv_lines:
        if project_name in dotenv_line:
            project_dotenv_line = dotenv_line
            break

    if not project_dotenv_line:
        print(f'Unable to find dotenv for project {project_name}')
        raise FileNotFoundError

    # Convert the ';' delimited k=v pairs into a dictionary
    dotenv_kv_pairs = project_dotenv_line.split(';')
    dotenv = {}
    for dotenv_kv_pair in dotenv_kv_pairs:
        if '=' not in dotenv_kv_pair:
            continue
        key = dotenv_kv_pair.split('=')[0]
        val = dotenv_kv_pair.split('=')[1]
        dotenv.update({key: val})
    return dotenv
