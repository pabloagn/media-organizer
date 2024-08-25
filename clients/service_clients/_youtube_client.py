# clients/service_clients/youtube_client.py

from googleapiclient.discovery import build
from utils import SingletonLogger, ConfigReader, CredentialHandler

class YouTubeClient:
    def __init__(self):
        self.logger = SingletonLogger.get_logger()
        self.config = ConfigReader().read_config()
        self.credentials = CredentialHandler().get_service_credentials('youtube')
        self.youtube = self._setup_youtube()

    def _setup_youtube(self):
        api_key = self.credentials['api_key']
        return build('youtube', 'v3', developerKey=api_key)

    def search_music_video(self, query):
        try:
            request = self.youtube.search().list(
                q=query,
                type='video',
                part='id,snippet',
                videoCategoryId='10',  # Music category
                maxResults=10
            )
            return request.execute()
        except Exception as e:
            self.logger.error(f"YouTube search error for query '{query}': {str(e)}")
            raise

    def get_video_details(self, video_id):
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            )
            return request.execute()
        except Exception as e:
            self.logger.error(f"YouTube error getting details for video ID '{video_id}': {str(e)}")
            raise

    # Add more methods as needed