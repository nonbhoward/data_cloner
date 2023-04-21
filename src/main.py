# imports, project
from src.config_reader.config_reader import read_config
from src.managers.cloner_manager import ClonerManager

config = read_config()
cm = ClonerManager(config=config)
while cm.cloners_active:
    cm.run()
