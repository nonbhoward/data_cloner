# Cloner to fetch data from Google Drive

# imports, python
import os

# imports, third-party
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


class GoogleDriveCloner:
    # Class attributes
    _ACTIVE = True
    _NAME = 'GoogleDrive'
    _SECRETS = 'credentials.json'
    _TOKEN = 'token.json'

    def __init__(self):
        # TODO cache write/load
        self._drive_metadata = None
        self._service = None

    def run(self):
        self.authenticate()
        self.read_drive_metadata()
        # 1. (in progress) Get a list of all files on the drive
        # 2. Get a list of all files backed up locally
        # 3. Comparing the lists, get a list of files to fetch from drive
        # 4. Fetch the files, writing them locally
        # 5. Track bandwidth usage and report it to the cloner manager

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

    def download(self):
        pass

    @property
    def drive_metadata(self) -> dict:
        return self._drive_metadata

    @drive_metadata.setter
    def drive_metadata(self, value: dict):
        self._drive_metadata = value

    @property
    def name(self) -> str:
        return self._NAME

    def read_drive_metadata(self, page_size=10) -> dict:
        """Use the service object to access endpoints to the root url
          https://www.googleapis.com

        :param page_size: int: number of results to fetch per file list
          request
        :return: drive_metadata: dict: metadata of the drive contents
        """
        drive_metadata = {}

        unique_mime_types = []  # TODO delete this
        unique_file_types = []  # TODO delete this

        results_processed = page_size
        next_page_token, first_loop = None, True
        while next_page_token or first_loop:
            if first_loop:  # get initial results and page token
                first_loop = False
                results = self.service.files().list(
                    pageSize=page_size
                ).execute()
                next_page_token = results['nextPageToken']
            else:  # apply fetched page token
                results = self.service.files().list(
                    pageSize=10,
                    pageToken=next_page_token
                ).execute()

            if 'files' not in results:
                continue

            # Process resulting files
            print(f'Processing results page {results_processed}')
            results_processed += page_size
            for file in results['files']:
                if file['mimeType'] not in unique_mime_types:
                    unique_mime_types.append(file['mimeType'])
                if file['kind'] not in unique_file_types:
                    unique_file_types.append(file['kind'])
                drive_metadata.update({
                    file['id']: {
                        'kind': file['kind'],
                        'mime_type': file['mimeType'],
                        'name': file['name']
                    }
                })

        return drive_metadata

    @property
    def service(self) -> Resource:
        return self._service

    @service.setter
    def service(self, value: Resource):
        self._service = value
