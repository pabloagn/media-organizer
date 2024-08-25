# clients/service_clients/service_clients.py

from utils import SingletonLogger, ConfigReader, CredentialHandler
from ._plex_client import PlexClient
import requests

class ServiceClients:
    def __init__(self):
        """Initialize ServiceClients with logger, config, and credentials."""
        self.logger = SingletonLogger.get_logger()
        self.config = ConfigReader().read_config()
        self.credentials = CredentialHandler().get_credentials()
        self.plex = None

    def initialize_client(self, client_name):
        """
        Initialize a specific client.

        :param client_name: Name of the client to initialize
        """
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
        """
        Get a client instance, initializing it if necessary.

        :param client_name: Name of the client to get
        :return: Client instance
        """
        client = getattr(self, client_name, None)
        if client is None:
            self.initialize_client(client_name)
            client = getattr(self, client_name)
        return client

    def search_music(self, query, libtype='artist'):
        """
        Search for music in the Plex library.

        :param query: Search query
        :param libtype: Type of library item to search for (default: 'artist')
        :return: Search results
        """
        self.logger.debug(f"Searching for music: query={query}, libtype={libtype}")
        result = self.get_client('plex').search_music(query, libtype)
        self.logger.debug(f"Search result: {result}")
        return result

    def get_playlist(self, playlist_name):
        """
        Get a playlist by name from Plex.

        :param playlist_name: Name of the playlist to retrieve
        :return: Playlist object
        """
        self.logger.debug(f"Getting playlist: {playlist_name}")
        playlist = self.get_client('plex').get_playlist(playlist_name)
        self.logger.debug(f"Retrieved playlist: {playlist}")
        return playlist

    def download_track(self, track, album_path, keep_original_name=True):
        """
        Download a track from Plex.

        :param track: Track object to download
        :param album_path: Path to save the track
        :param keep_original_name: Whether to keep the original filename
        :return: True if download was successful, False otherwise
        """
        self.logger.debug(f"Attempting to download track: {track.title}")
        self.logger.debug(f"Album path: {album_path}")
        self.logger.debug(f"Keep original name: {keep_original_name}")
        try:
            track.download(album_path, keep_original_name=keep_original_name)
            self.logger.info(f"Successfully downloaded track: {track.title}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to download track {track.title}: {str(e)}")
            return False

    def download_album_cover(self, album, save_path):
        """
        Download an album cover from Plex.

        :param album: Album object
        :param save_path: Path to save the cover image
        :return: True if download was successful, False otherwise
        """
        self.logger.debug(f"Attempting to download album cover for: {album.title}")
        self.logger.debug(f"Save path: {save_path}")
        result = self.get_client('plex').download_album_cover(album, save_path)
        self.logger.debug(f"Album cover download result: {result}")
        return result

    def download_artist_image(self, artist, cover_path):
        """
        Download an artist image from Plex.

        :param artist: Artist object
        :param cover_path: Path to save the artist image
        :return: True if download was successful, False otherwise
        """
        self.logger.debug(f"Attempting to download artist image for: {artist.title}")
        self.logger.debug(f"Cover path: {cover_path}")
        try:
            if artist.thumb:
                # Get the full URL for the thumb
                thumb_url = self.get_client('plex').server.url(artist.thumb, includeToken=True)
                # Download the image using requests
                import requests
                response = requests.get(thumb_url)
                if response.status_code == 200:
                    with open(cover_path, 'wb') as f:
                        f.write(response.content)
                    self.logger.info(f"Successfully downloaded artist image for: {artist.title}")
                    return True
                else:
                    self.logger.warning(f"Failed to download artist image for {artist.title}. Status code: {response.status_code}")
                    return False
            else:
                self.logger.warning(f"No thumb available for artist: {artist.title}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to download artist image for {artist.title}: {str(e)}")
            return False

    def get_artist_albums(self, artist):
        """
        Get all albums for an artist from Plex.

        :param artist: Artist object
        :return: List of album objects
        """
        self.logger.debug(f"Getting albums for artist: {artist.title}")
        albums = self.get_client('plex').get_artist_albums(artist)
        self.logger.debug(f"Retrieved {len(albums)} albums for {artist.title}")
        return albums

def get_album_tracks(self, album):
        """
        Get all tracks for an album from Plex.

        :param album: Album object
        :return: List of track objects
        """
        self.logger.debug(f"Getting tracks for album: {album.title}")
        tracks = self.get_client('plex').get_album_tracks(album)
        self.logger.debug(f"Retrieved {len(tracks)} tracks for {album.title}")
        return tracks