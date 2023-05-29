# Cloner to fetch data from Google Drive

# imports, python
import os

# imports, third-party
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource

# imports, project
from src.managers.config_manager import ConfigManager

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


class GoogleDriveCloner:
    # Class attributes
    _ACTIVE = True
    _FOLDER_NAME = 'GoogleDrive'
    _NO_MORE_PAGES = '__THERE_ARE_NO_MORE_PAGES__'
    _SECRETS = 'credentials.json'
    _TOKEN = 'token.json'

    def __init__(self, config_manager: ConfigManager):
        print(f'Initializing {self.__class__.__name__}')
        # TODO cache write/load
        self._config_manager = config_manager
        self._drive_metadata = {}
        self._next_page_token = ''
        self._results_processed = 0
        self._service = None

        # TODO delete or property below
        self._unique_mime_types = []
        self._unique_file_types = []

    def run(self):
        self.authenticate()

        # 1. Get a list of all files on the drive
        while self.next_page_token is not self._NO_MORE_PAGES:
            self.read_drive_metadata(page_size=10)
            # FIXME, remove this dev line
            if len(self.drive_metadata) > 10:
                break

        # 1a. Download a test file
        for file_id, file_metadata in self.drive_metadata.items():
            self.download(
                file_id=file_id,
                file_metadata=file_metadata
            )
        # 2. Get a list of all files backed up locally
        # 3. Comparing the lists, get a list of files to fetch from drive
        # 4. Fetch the files, writing them locally
        # 5. Track bandwidth usage and report it to the cloner manager
        if self.next_page_token is self._NO_MORE_PAGES:
            self.reset()

        print(f'Cloner task finished : {self.__class__.__name__}')

    @property
    def active(self):
        return self._ACTIVE

    @active.setter
    def active(self, value):
        print(f"Do not set this attribute, discarding value : {value}")

    def authenticate(self):
        """Basic auth using the Drive v3 API."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self._TOKEN):
            creds = Credentials.from_authorized_user_file(self._TOKEN, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # FIXME this always seems to fail, delete token.json to resolve
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self._SECRETS, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self._TOKEN, 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

    def cache_create_new(self):
        pass

    def cache_delete(self):
        pass

    def cache_refresh(self):
        pass

    def download(self, file_id: str, file_metadata: dict):
        """Export the byte_content of a file from the workspace. Note that
          the api limits the byte_content to 10MiB per export.

        # TODO, are there any files greater than 10MiB on the workspace?

        :param file_id: the id of a file on the remote drive.
        :param file_metadata: data about the file to export/download.
        :return: byte content of a file to be written to disk
        """
        mime_type = file_metadata['mime_type']
        byte_content = self.service.files().export(
            fileId=file_id,
            mimeType=mime_type
        )

    @property
    def drive_metadata(self) -> dict:
        return self._drive_metadata

    @drive_metadata.setter
    def drive_metadata(self, value: dict):
        self._drive_metadata = value

    @property
    def next_page_token(self) -> str:
        return self._next_page_token

    @next_page_token.setter
    def next_page_token(self, value: str):
        self._next_page_token = value

    def read_drive_metadata(self, page_size=10) -> None:
        """Use the service object to access endpoints to the root url
          https://www.googleapis.com

        :param page_size: int: result count to fetch per request
        """

        results = None
        try:
            results = self.service.files().list(
                pageSize=page_size,
                pageToken=self.next_page_token
            ).execute()
        except Exception as exc:
            # TODO add functionality to allow resume after http errors
            print(f'{exc}')

        if not results:
            print(f'service.files.list api call failed, possibly due to a '
                  f'network error')
            return

        if 'files' in results:
            # Iterate through files metadata
            for file in results['files']:

                # Record unique types
                if file['mimeType'] not in self._unique_mime_types:
                    self._unique_mime_types.append(file['mimeType'])
                if file['kind'] not in self._unique_file_types:
                    self._unique_file_types.append(file['kind'])

                # Record files metadata
                self.drive_metadata.update({
                    file['id']: {
                        'kind': file['kind'],
                        'mime_type': file['mimeType'],
                        'name': file['name']
                    }
                })  # Exit for loop
            self.results_processed += len(results['files'])
            print(f'Total objects encountered : {self.results_processed}')

        # Fetch ref to next page
        if 'nextPageToken' not in results:
            self.next_page_token = self._NO_MORE_PAGES
            return  # No more pages
        self.next_page_token = results['nextPageToken']

    def reset(self):
        """A place to reset class information in the case of subsequent runs.
          May not be needed
        """
        print("TODO delete this function if possible")
        self.next_page_token = ''

    @property
    def results_processed(self) -> int:
        return self._results_processed

    @results_processed.setter
    def results_processed(self, value: int):
        self._results_processed = value

    @property
    def service(self) -> Resource:
        return self._service

    @service.setter
    def service(self, value: Resource):
        self._service = value
