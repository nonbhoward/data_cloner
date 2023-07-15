# Management related to app configuration

# imports, python
from os import getenv
from os.path import exists
from pathlib import Path

# imports, third-party
import yaml

# imports, project
from src.util.util import find_content_root


# Constants
# default_project_name: The folder containing the project files. Used
#   to determine the content_root to avoid relying on relative directory
#   navigation.
default_project_name = 'data_cloner'

# Error messages
# TODO there is a lot of repetition in the use of these values,
#   think about how this could be reduced
setter_message_no_value = f"No value passed to setter"
setter_message_bad_type = f"Bad type for setter"


class ConfigManager:
    def __init__(self, path_to_config='', project_name=''):
        print(f'Initializing {self.__class__.__name__}')
        self._config = self.read_config(path_to_config=path_to_config,
                                        project_name=project_name)
        self._dotenv = None

    @property
    def cloner_manager(self, key: str = 'ClonerManager') -> dict:
        if key not in self._config:
            print(f'No entry found for key : {key}')
            return {}
        return self._config[key]

    @property
    def file_manager(self, key: str = 'FileManager') -> dict:
        if key not in self._config:
            print(f'No entry found for key : {key}')
            return {}
        return self._config[key]

    @staticmethod
    def read_config(path_to_config='', project_name='') -> dict:
        """Read the configuration file.
        Get the path to the configuration file, load it, store it. Avoiding
          dependency on relative paths.

        :param path_to_config: override automatically finding config.
        :param project_name: override default project name.
        :return: yaml_cfg: dict: The config dictionary."""

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

    @property
    def content_root(self) -> Path:
        return self._config['paths']['content_root']

    @content_root.setter
    def content_root(self, value):
        validate_setter_value(value=value, type_requirement=Path)
        self._config['paths']['content_root'] = value

    @property
    def destroy_remote(self) -> list:
        return self._config['ClonerManager']['destroy_remote']

    @property
    def dotenv(self) -> dict:
        return self._config['dotenv']

    @dotenv.setter
    def dotenv(self, value: dict):
        # TODO delete this function if unused under the rationale that
        #   any use of this function would be highly prone to breaking
        #   something as well as general bad practice.
        self._config['dotenv'] = value

    @property
    def enabled_cloners(self) -> list:
        """A list of strings indicating cloners that are expected to run."""
        return self._config['ClonerManager']['enabled_cloners']

    @enabled_cloners.setter
    def enabled_cloners(self, value: list):
        """Same description as property"""
        validate_setter_value(value=value, type_requirement=list)
        self._config['ClonerManager']['enabled_cloners'] = value


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
    # TODO would be nice if this direct assignment could be moved to the
    #   config manager
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


def validate_setter_value(value, type_requirement: type):
    assert value, setter_message_no_value
    assert isinstance(value, type_requirement), setter_message_bad_type
