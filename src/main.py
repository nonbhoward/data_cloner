# imports, python
import os

# imports, project
from src.managers.cloner_manager import ClonerManager
from src.managers.config_manager import ConfigManager


def main():
    config_manager = ConfigManager()

    # Change the working directory to the content root
    os.chdir(config_manager.content_root)

    cm = ClonerManager(config_manager=config_manager)
    while cm.cloners_to_run:
        cm.run()


if __name__ == '__main__':
    main()
