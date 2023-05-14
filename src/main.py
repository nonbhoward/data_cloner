# imports, python
import os

# imports, project
from src.managers.cloner_manager import ClonerManager
from src.managers.config_manager import ConfigManager
from src.managers.data_manager import DataManager
from src.managers.metadata_manager import MetadataManager


def main():
    config_manager = ConfigManager()

    # Change the working directory to the content root
    os.chdir(config_manager.content_root)

    # data_manager = DataManager(config_manager=config_manager)
    # metadata_manager = MetadataManager(config_manager=config_manager)
    cloner_manager = ClonerManager(config_manager=config_manager)

    cloner_metadata = cloner_manager.run()

    # metadata_manager.run(cloner_metadata=cloner_metadata)
    # data_manager.run(cloner_metadata=cloner_metadata)


if __name__ == '__main__':
    main()
