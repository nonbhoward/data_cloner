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
        self._service = None

    def run(self):
        self.authenticate()
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        pass

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
    def name(self) -> str:
        return self._NAME

    @property
    def service(self) -> Resource:
        return self._service

    @service.setter
    def service(self, value: Resource):
        self._service = value
