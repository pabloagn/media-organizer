# clients/service_clients/service_clients.py

from utils import SingletonLogger, ConfigReader, CredentialHandler
from ._plex_client import PlexClient

class ServiceClients:
    def __init__(self):
        self.logger = SingletonLogger.get_logger()
        self.config = ConfigReader().read_config()
        self.credentials = CredentialHandler().get_credentials()
        self.plex = None

    def initialize_client(self, client_name):
        try:
            if client_name == 'plex':
                self.logger.info("Initializing Plex client")
                self.plex = PlexClient(self.config, self.credentials)
            else:
                raise ValueError(f"Unknown client: {client_name}")
           
            self.logger.info(f"Initialized {client_name} client successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize {client_name} client: {str(e)}")
            raise

    def get_client(self, client_name):
        client = getattr(self, client_name, None)
        if client is None:
            self.initialize_client(client_name)
            client = getattr(self, client_name)
        return client

    # Plex-specific methods
    def search_music(self, query, libtype='artist'):
        return self.get_client('plex').search_music(query, libtype)

    def get_playlist(self, playlist_name):
        return self.get_client('plex').get_playlist(playlist_name)

    def download_track(self, track, save_path, keep_original_name=False):
        return self.get_client('plex').download_track(track, save_path, keep_original_name)

    def download_album_cover(self, album, save_path):
        return self.get_client('plex').download_album_cover(album, save_path)

    def get_artist_albums(self, artist):
        return self.get_client('plex').get_artist_albums(artist)

    def get_album_tracks(self, album):
        return self.get_client('plex').get_album_tracks(album)

    # Methods for other services can be added here as needed