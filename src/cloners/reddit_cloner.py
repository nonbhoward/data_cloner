# Cloner to fetch data from Reddit

# imports, python
from pathlib import Path
from time import sleep
import json
import os
import random
import requests

# imports, third-party
import praw

# imports, project
from src.managers.config_manager import ConfigManager


class RedditDataCloner:
    _ACTIVE = True
    _FOLDER_NAME = 'RedditData'

    def __init__(self, config_manager: ConfigManager):
        print(f'Initializing {self.__class__.__name__}')
        self._config_manager = config_manager
        self._delay_per_download = 15
        self._destroy_remote = False
        self._path_to_reddit_media = None
        self._submissions_per_request = 2
        self._reddit = None
        self._subreddit = None

        self.top_submissions_metadata = {}

        # Check if remote data deletion is enabled
        key = 'destroy_remote'
        if key in self._config_manager.config:
            remotes_to_destroy = self._config_manager.config[key]
            if self.__class__.__name__ in remotes_to_destroy:
                self._destroy_remote = True

    def authenticate(self):
        """
        This will authenticate with whatever API and be different for each
          cloner.
        """
        # Load dotenv to local environment, convenience variable
        dotenv = self._config_manager.dotenv

        client_id = dotenv['client_id']
        client_secret = dotenv['client_secret']
        password = dotenv['password']
        user_agent = dotenv['user_agent']
        username = dotenv['username']

        self._reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            user_agent=user_agent,
            username=username
        )

    def configure(self):
        # Configure the subreddit target
        target_subreddit = self._config_manager.dotenv['subreddit']
        self._subreddit = self._reddit.subreddit(target_subreddit)

        # Configure the local data path
        path_to_downloads = Path(os.environ.get('HOME'), 'Downloads')
        path_to_data_cloner = Path(path_to_downloads, 'data_cloner')
        if not os.path.exists(path_to_data_cloner):
            os.mkdir(path_to_data_cloner)
        path_to_reddit_media = Path(path_to_data_cloner, self._FOLDER_NAME)
        if not os.path.exists(path_to_reddit_media):
            os.mkdir(path_to_reddit_media)
        self._path_to_reddit_media = path_to_reddit_media

    def run(self, destroy=False):
        """The primary action for this class"""
        self.authenticate()
        self.configure()

        # 1. Fetch metadata
        self.fetch_and_parse_submissions()
        # 2. Attempt to download remote file
        self.clone_remote_data()
        # 3. Confirm remote file download success
        # 4. Delete the remote
        if self._destroy_remote:
            self.destroy_remote()

        print(f'Cloner task finished : {self.__class__.__name__}')

    def clone_remote_data(self):
        for sub_id, sub_metadata in self.top_submissions_metadata.items():
            url = None
            if 'url' in sub_metadata:
                url = sub_metadata['url']
            if not url:
                continue  # Skip if missing url
            response = requests.get(url=url)
            parsed_response = self.parse_response(response=response,
                                                  sub_metadata=sub_metadata)
            self.wait_between_downloads()

    def destroy_remote(self):
        pass

    def fetch_and_parse_submissions(self):
        # Fetch remote submission data
        submission_listing_generator = \
            self._subreddit.top(
                time_filter="all",
                limit=self._submissions_per_request
            )

        # Parse submission metadata
        top_submissions_metadata = {}
        for submission_listing in submission_listing_generator:
            # Extract metadata
            submission_metadata = extract_submission_metadata(
                submission_listing=submission_listing)

            guid_ext = random.randint(100, 999)
            submission_guid = submission_metadata['id'] + f'_{guid_ext}'
            top_submissions_metadata.update({
                submission_guid: submission_metadata
            })

        # Store data to class
        self.top_submissions_metadata = top_submissions_metadata

    def parse_response(self, response, sub_metadata) -> dict:
        content, url = None, None
        if hasattr(response, 'url'):
            url = response.url
        if hasattr(response, 'content'):
            content = response.content
        if content and url and url.endswith('.jpg'):
            self.save_file(content=content, sub_metadata=sub_metadata)

    def save_file(self, content, sub_metadata):
        path_to_reddit_media = self._path_to_reddit_media
        pass

    def wait_between_downloads(self):
        for i in range(self._delay_per_download, 0):
            print(f"Waiting {self._delay_per_download} : {i}")
            sleep(1)


def extract_submission_metadata(submission_listing) -> dict:
    sl_author = parse_author_name(submission_listing=submission_listing)
    sl_created = parse_time_created(submission_listing=submission_listing)
    sl_comments = parse_comments(submission_listing=submission_listing)
    sl_id = parse_id(submission_listing=submission_listing)
    sl_media = parse_media(submission_listing=submission_listing)
    sl_url = parse_url(submission_listing=submission_listing)
    submission_metadata = {
        'author': sl_author,
        'comments': sl_comments,
        'created_utc': sl_created,
        'id': sl_id,
        'media': sl_media,
        'url': sl_url
    }
    return submission_metadata


def parse_author_name(submission_listing) -> str:
    if not submission_listing:
        return 'no_submission_listing'

    if not hasattr(submission_listing, 'author'):
        return 'no_submission_listing.author'

    if not hasattr(submission_listing.author, 'name'):
        return 'no_submission_listing.author.name'

    print(f'Author name parsed : {submission_listing.author.name}')
    return submission_listing.author.name


def parse_comments(submission_listing) -> dict:
    comment_metadata = {}
    if not hasattr(submission_listing, 'comments'):
        return {}
    comments = submission_listing.comments._comments
    for comment in comments:

        # Attribute fallbacks to prevent missing attribute errors
        comment_body = 'no_comment_body'
        comment_link_id = 'no_comment_link_id'
        comment_name = 'no_comment_name'
        comment_parent_id = 'no_comment_parent_id'
        comment_permalink = 'no_comment_permalink'
        if hasattr(comment, 'body'):
            comment_body = comment.body
        if hasattr(comment, 'link_id'):
            comment_link_id = comment.link_id
        if hasattr(comment, 'name'):
            comment_name = comment.name
        if hasattr(comment, 'parent_id'):
            comment_parent_id = comment.parent_id
        if hasattr(comment, 'permalink'):
            comment_permalink = comment.permalink

        comment_metadata.update({
            comment.id: {
                'body': comment_body,
                'link_id': comment_link_id,
                'name': comment_name,
                'parent_id': comment_parent_id,
                'permalink': comment_permalink
            }
        })

    if not hasattr(submission_listing, 'id'):
        message = 'Inspect the object that caused this because it should ' \
                  'never happen'
        print(f'{message}')
        breakpoint()  # TODO delete this after dev
        return comment_metadata
    print(f'Finished parsing comments from submission {submission_listing.id}')
    return comment_metadata


def parse_id(submission_listing) -> str:
    if not submission_listing:
        return 'no_submission_listing'
    sl_id = 'no_submission_listing_id'
    if hasattr(submission_listing, 'id'):
        sl_id = submission_listing.id
    print(f'Id parsed : {sl_id}')
    return sl_id


def parse_media(submission_listing) -> dict:
    media_metadata = {}
    if not submission_listing:
        return {'error': 'no_submission_listing'}
    if not hasattr(submission_listing, 'media'):
        return {'error': 'no_submission_listing.media'}
    if not submission_listing.media:
        return {'error': 'submission_listing.media_is_none'}
    if 'oembed' not in submission_listing.media:
        return {'error': 'no_submission_listing.media.oembed'}

    media = submission_listing.media['oembed']

    media_author_name = 'no_media_author_name'
    media_author_url = 'no_media_author_url'
    media_height = 'no_media_height'
    media_html = 'no_media_html'
    media_provider_name = 'no_media_provider_name'
    media_provider_url = 'no_media_provider_url'
    media_title = 'no_media_title'
    media_width = 'no_media_width'

    if 'author_name' in media:
        media_author_name = media['author_name']
    if 'author_url' in media:
        media_author_url = media['author_url']
    if 'height' in media:
        media_height = media['height']
    if 'html' in media:
        media_html = media['html']
    if 'provider_name' in media:
        media_provider_name = media['provider_name']
    if 'provider_url' in media:
        media_provider_url = media['provider_url']
    if 'title' in media:
        media_title = media['title']
    if 'width' in media:
        media_width = media['width']

    media_metadata.update({
        'author_name': media_author_name,
        'author_url': media_author_url,
        'height': media_height,
        'html': media_html,
        'provider_name': media_provider_name,
        'provider_url': media_provider_url,
        'title': media_title,
        'width': media_width
    })

    print(f'Finished parsing media metadata from submission listing')
    return media_metadata


def parse_time_created(submission_listing) -> str:
    time_created = float(123456789)
    if hasattr(submission_listing, 'created_utc'):
        time_created = submission_listing.created_utc
    print(f'Parsed time created : {time_created}')
    return time_created


def parse_url(submission_listing) -> str:
    url = 'no_url_found'
    if hasattr(submission_listing, 'url'):
        url = submission_listing.url
    print(f'Parsed url : {url}')
    return url
