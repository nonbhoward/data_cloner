# Cloner to fetch data from Reddit

# imports, python
from html.parser import HTMLParser
from pathlib import Path
from time import sleep
import json
import os
import requests

# imports, third-party
import praw

# imports, project
from src.managers.config_manager import ConfigManager


class MyGifvParser(HTMLParser):
    def __init__(self, raw_html):
        super().__init__()
        self.data = []
        self.links = []
        self.raw_html = raw_html.decode()
        self.feed(self.raw_html)
        self.parse_links()

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        if 'gifUrl' in data:
            self.data.append(data)
            return

    def parse_links(self):
        for data in self.data:
            try:
                d_elements = data.split('\n')
                content_string = d_elements[5].strip()
                c_elements = content_string.split(' ')
                c_elements = [element for element in c_elements if element]
                content_link = c_elements[1].replace(',', '').replace('\"', '').replace('\'', '')[2:]
            except Exception as exc:
                content_link = None
            if not content_link:
                continue
            if content_link not in self.links:
                self.links.append(content_link)


class MyRedParser(HTMLParser):
    def __init__(self, raw_html):
        super().__init__()
        self.data = []
        self.links = []
        self.raw_html = raw_html.decode()
        self.feed(self.raw_html)
        self.parse_links()

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        if 'context' not in data:
            return
        self.data.append(data)

    def parse_links(self):
        for data in self.data:
            d_elements = data.split(',')
            content_string = [data for data in d_elements if 'contentUrl' in data][0]
            data_link = content_string.split('\"')[3]
            if data_link in self.links:
                continue
            self.links.append(data_link)


class RedditDataCloner:
    _ACTIVE = True
    _FOLDER_NAME = 'RedditData'

    def __init__(self, config_manager: ConfigManager):
        print(f'Initializing {self.__class__.__name__}')
        self._config_manager = config_manager
        self._delay_per_action = 3
        self._destroy_remote = False
        self._path_to_reddit_media = None
        self._submissions_per_request = 1000
        self._reddit = None
        self._submissions_to_destroy = []
        self._subreddit = None

        self.top_submissions_metadata = {}

        # Check if remote data deletion is enabled
        key = 'destroy_remote'
        if key in self._config_manager.config:
            remotes_to_destroy = self._config_manager.config[key]
            if self.__class__.__name__ in remotes_to_destroy:
                self._destroy_remote = True

    def run(self, destroy=False):
        """The primary action for this class"""
        self.authenticate()
        self.configure()

        # 1. Fetch metadata
        self.fetch_and_parse_submissions()
        # 2. Attempt to download remote file
        self.save_data_to_disk()
        # 3. Confirm remote file download success
        # 4. Delete the remote
        self._destroy_remote = True  # TODO delete
        if self._destroy_remote:
            self.destroy_remote()

        print(f'Cloner task finished : {self.__class__.__name__}')

    # RUN-LEVEL FUNCTION
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

    # RUN-LEVEL FUNCTION
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

    # RUN-LEVEL FUNCTION
    def fetch_and_parse_submissions(self):
        # Fetch remote submission data
        submission_listing_generator = \
            self._subreddit.top(
                time_filter="all",
                limit=self._submissions_per_request
            )

        # Parse submission metadata
        top_submissions_metadata = {}
        submissions_processed = 0
        for submission_listing in submission_listing_generator:
            submissions_processed += 1
            print(f'Processing submission : {submissions_processed} / {self._submissions_per_request}')
            # Extract metadata
            submission_metadata = extract_submission_metadata(
                submission_listing=submission_listing)

            submission_guid = submission_metadata['id']
            top_submissions_metadata.update({
                submission_guid: submission_metadata
            })

        # Store data to class
        self.top_submissions_metadata = top_submissions_metadata

    # RUN-LEVEL FUNCTION
    def save_data_to_disk(self):
        submission_count = len(self.top_submissions_metadata)
        submission_number = 0
        for sub_id, sub_metadata in self.top_submissions_metadata.items():
            submission_number += 1
            url = None
            if 'url' in sub_metadata:
                url = sub_metadata['url']
            if not url:
                continue  # Skip if missing url
            print(f'Attempting to process url : {url}, submission {submission_number} / {submission_count}')
            try:
                response = requests.get(url=url)
            except Exception as exc:
                print(f'Exception encountered processing {sub_id} : {sub_metadata}')
                continue
            self.parse_response_and_save_data(
                response=response,
                sub_metadata=sub_metadata
            )
            self.wait_btw_actions()

    # RUN-LEVEL FUNCTION
    def destroy_remote(self):
        submissions_to_destroy = []
        for sl_id in self._submissions_to_destroy:
            submission = self._reddit.submission(sl_id)
            submissions_to_destroy.append(submission)

        remove_count = len(submissions_to_destroy)
        removed = 0
        for submission_to_destroy in submissions_to_destroy:
            submission_to_destroy.mod.remove()
            removed += 1
            print(f'Successfully removed : {submission_to_destroy}, {removed} / {remove_count}')
            self.wait_btw_actions()
        pass

    # SUB-RUN FUNCTION
    def parse_response_and_save_data(self, response, sub_metadata):
        content, status_code, url = None, None, None
        if hasattr(response, 'status_code'):
            status_code = response.status_code
        if hasattr(response, 'url'):
            url = response.url
        if hasattr(response, 'content'):
            content = response.content
        if status_code != 200:
            return

        # Extract extension
        try:
            extension = '.' + url.split('.')[-1]
        except Exception as exc:
            print(f'No extension found for {url}')
            extension = None

        # TODO Flag to catch edge-cases.. hopefully  never triggers
        # Process url.split() throws exception
        if extension is None:
            print(f'Extension is none for url : {url}')
            breakpoint()
            return  # Exception thrown

        # Process jpeg, gif
        supported_extensions = ['.gif', '.jpg', '.png']
        if content and url and extension in supported_extensions:
            print(f'Processing url : {url}')
            self.save_file_and_update_destroy_metadata(
                response=response,
                sub_metadata=sub_metadata,
                ext=extension
            )
            return  # jpg, gif, png return

        special_extensions = ['.gifv']
        if content and url and extension in special_extensions:
            print(f'Special ext encountered at : {url}')
            gifv_parser = MyGifvParser(raw_html=content)
            if not hasattr(gifv_parser, 'links'):
                return  # Error, attr missing
            if not gifv_parser.links:
                return  # Failed, no links found
            try:
                response = requests.get(url=gifv_parser.links[0])
            except Exception as exc:
                print(f"Request failed for url : {url}")
                return
            self.save_file_and_update_destroy_metadata(
                response=response,
                sub_metadata=sub_metadata,
                ext='.gif'
            )
            return  # gifv to gif return

        if 'gifs' in url and 'watch' in url:
            print(f'Red encountered at : {url}')
            red_parser = MyRedParser(raw_html=content)
            if not hasattr(red_parser, 'links'):
                return  # Error, attr missing
            if not red_parser.links:
                return  # Fail, no links found
            try:
                response = requests.get(url=red_parser.links[0])
            except Exception as exc:
                print(f"Request failed for url : {url}")
                return
            self.save_file_and_update_destroy_metadata(
                response=response,
                sub_metadata=sub_metadata,
                ext='.mp4'
            )
            return  # red to mp4 return

        # TODO process cat
        if 'https' in url and 'gfycat' in url:
            print(f'Cat encountered at : {url}')
            return  # Non-critical target return

        print(f'New file type encountered. Url : {url}')

    # SUB-RUN FUNCTION
    def save_file_and_update_destroy_metadata(self, response, sub_metadata, ext):
        content = response.content

        # Build path to media
        path_to_reddit_media = self._path_to_reddit_media
        if 'id' not in sub_metadata:
            print(f'Cannot save file : {sub_metadata}')
            return
        sl_id = sub_metadata['id']

        path_to_save_submission_data = Path(path_to_reddit_media, sl_id)

        if not os.path.exists(path_to_save_submission_data):
            os.mkdir(path_to_save_submission_data)

        # Build file name
        if 'author' not in sub_metadata:
            print(f'No author : {sub_metadata}')
            return

        if 'created_utc' not in sub_metadata:
            print(f'No creation time : {sub_metadata}')
            return

        file_name_to_write = str(sub_metadata['created_utc']) + '_' + sub_metadata['author'] + ext
        path_to_write_file = Path(path_to_save_submission_data, file_name_to_write)

        # Write file
        with open(path_to_write_file, 'wb') as ftw:
            ftw.write(content)
            print(f'Successfully wrote : {path_to_write_file}')

        # Build metadata name
        metadata_file_name = file_name_to_write + '_metadata' + '.json'
        path_to_write_metadata = Path(path_to_save_submission_data, metadata_file_name)

        # Write metadata
        with open(path_to_write_metadata, 'w') as mtw:
            json.dump(sub_metadata, mtw)
            print(f'Successfully wrote : {path_to_write_metadata}')

        # Confirm files saved
        all_files = []
        for root, dirs, files in os.walk(path_to_reddit_media):
            for file in files:
                all_files.append(Path(root, file))

        if path_to_write_file not in all_files:
            return
        print(f'Confirmed file written')

        if path_to_write_metadata not in all_files:
            return
        print(f'Confirmed metadata written')

        # Create deletion metadata, save to class to be dumped to disk
        self._submissions_to_destroy.append(sl_id)

    # SUB-RUN FUNCTION
    def wait_btw_actions(self):
        for i in range(self._delay_per_action):
            print(f"Waiting {self._delay_per_action} second(s) : {i}")
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
