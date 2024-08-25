# clients/service_clients/musicbrainz_client.py

import musicbrainzngs
from utils import SingletonLogger, ConfigReader, CredentialHandler

class MusicBrainzClient:
    def __init__(self):
        self.logger = SingletonLogger.get_logger()
        self.config = ConfigReader().read_config()
        self.credentials = CredentialHandler().get_service_credentials('musicbrainz')
        self._setup_musicbrainz()

    def _setup_musicbrainz(self):
        musicbrainzngs.set_useragent(
            self.config['musicbrainz']['app_name'],
            self.config['musicbrainz']['version'],
            self.config['musicbrainz']['contact']
        )

    def search_artist(self, artist_name):
        try:
            return musicbrainzngs.search_artists(artist=artist_name)
        except musicbrainzngs.WebServiceError as e:
            self.logger.error(f"MusicBrainz search error for artist '{artist_name}': {str(e)}")
            raise

    def get_artist_albums(self, artist_id):
        try:
            return musicbrainzngs.browse_releases(artist=artist_id, release_type=['album', 'ep'])
        except musicbrainzngs.WebServiceError as e:
            self.logger.error(f"MusicBrainz error getting albums for artist ID '{artist_id}': {str(e)}")
            raise

    def search_release(self, release_name, artist_name=None):
        try:
            return musicbrainzngs.search_releases(release=release_name, artist=artist_name)
        except musicbrainzngs.WebServiceError as e:
            self.logger.error(f"MusicBrainz search error for release '{release_name}': {str(e)}")
            raise

    # Add more methods as needed