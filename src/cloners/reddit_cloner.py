# Cloner to fetch data from Reddit

# imports, third-party
import praw

# imports, project
from src.managers.config_manager import ConfigManager


class RedditDataCloner:
    _ACTIVE = True
    _FOLDER_NAME = 'RedditData'

    def __init__(self, config_manager: ConfigManager,
                 folder_extension: str):
        print(f'Initializing {self.__class__.__name__}')
        self._config_manager = config_manager
        self.reddit = None

        # TODO unused variables
        self._folder_extension = folder_extension

    def authenticate(self):
        """
        This will authenticate with whatever API and be different for each
          cloner.
        """
        # TODO test and validate this, add vals to dotenv
        # Load dotenv to local environment, convenience variable
        dotenv = self._config_manager.dotenv

        client_id = dotenv['client_id']
        client_secret = dotenv['client_secret']
        password = dotenv['password']
        user_agent = dotenv['user_agent']
        username = dotenv['username']

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            user_agent=user_agent,
            username=username
        )

