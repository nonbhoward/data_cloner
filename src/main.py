# imports, project
from src.managers.cloner_manager import ClonerManager
from src.managers.config_manager import ConfigManager


def main():
    config_manager = ConfigManager()
    cm = ClonerManager(config_manager=config_manager)
    while cm.cloners_active:
        cm.run()


if __name__ == '__main__':
    main()
