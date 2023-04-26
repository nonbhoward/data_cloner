# imports, python
from os import getcwd
from os import getenv
from os.path import exists
from pathlib import Path

# imports, third-party
import yaml

# Constants
# default_project_name: The folder containing the project files. Used
#   to determine the content_root to avoid relying on relative directory
#   navigation.
default_project_name = 'data_cloner'


def find_content_root(project_name='') -> Path:
    """Locate the project root, aka the content root, without relying on
        relative directories. The downside of this is that it relies on
        a defined project name to be found in the path.

    :param project_name: override default project name.
    :return: the path to the content root."""

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


def read_config(path_to_config='', project_name='') -> dict:
    """Read the configuration file.
    Get the path to the configuration file, load it, return it. Avoiding
      dependency on relative paths.

    :param path_to_config: override automatically finding config.
    :param project_name: override default project name.
    :return: The config dictionary."""

    if not project_name:
        project_name = default_project_name
    path_to_content_root = find_content_root(project_name=project_name)

    # Extend content root to locate configuration
    path_to_config = Path(path_to_config) if path_to_config \
        else Path(path_to_content_root, 'config', 'config.yaml')

    message = f"Path to config {path_to_config} does not exist"
    assert exists(path_to_config), message

    # Read the configuration
    with open(path_to_config, 'r') as cfg_r:
        yaml_cfg = yaml.safe_load(cfg_r)

    yaml_cfg.update({
        'names': {
            'project': project_name
        },
        'paths': {
            'content_root': path_to_content_root
        }
    })

    # Append dotenv to config dictionary and return
    # Store the content root path
    add_dotenv_to_config(config=yaml_cfg)

    return yaml_cfg


def add_dotenv_to_config(config, dotenv_filename='.env') -> dict:
    """Read information stored outside project.

    Format Example :
      project_name;key1=value1;key2=value2; ... ;keyN=valueN

    :param config: the project configuration.
    :param dotenv_filename: the filename containing the information.
    :return: dictionary containing the dotenv information for this project."""
    # Use project_name metadata to find content root
    path_to_home = Path(getenv('HOME'))
    path_to_dotenv = Path(path_to_home, dotenv_filename)

    with open(path_to_dotenv, 'r') as env_r:
        dotenv_lines = env_r.readlines()

    # Locate the dotenv line for this project
    project_name = config['names']['project']
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
        key = dotenv_kv_pair.split('=')[0].strip()
        val = dotenv_kv_pair.split('=')[1].strip()
        dotenv.update({key: val})

    config.update({
        'dotenv': dotenv,
    })

    return dotenv
