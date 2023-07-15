# imports, python
import os

# imports, project
from src.managers.cloner_manager import ClonerManager
from src.managers.config_manager import ConfigManager
from src.managers.data_manager import FileManager
from src.managers.metadata_manager import MetadataManager


def main():
    config_manager = ConfigManager()

    # Change the working directory to the content root
    # os.chdir(config_manager.content_root)

    # Initialize the data and metadata managers
    # TODO I dislike the seeming arbitrary hierarchy of managers, currently
    #   the cloner manager is the "chief" manager and it dispatches the others
    #   for various tasks but shouldn't there be some sort of inherent
    #   indication which object is the parent?
    file_manager = FileManager(config_manager=config_manager)
    metadata_manager = MetadataManager(config_manager=config_manager)

    # Initialize the core manager tha launches the cloners
    cloner_manager = ClonerManager(
        config_manager=config_manager,
        file_manager=file_manager,
        metadata_manager=metadata_manager
    )
    cloner_metadata = cloner_manager.run()

    # metadata_manager.run(cloner_metadata=cloner_metadata)
    # file_manager.run(cloner_metadata=cloner_metadata)


if __name__ == '__main__':
    main()
