# clients/service_clients/_plex_client.py

from plexapi.server import PlexServer
from utils import SingletonLogger

class PlexClient:
    def __init__(self, config, credentials):
        self.logger = SingletonLogger.get_logger()
        self.config = config
        self.credentials = credentials
        self.server = self._connect_to_plex()

    def _connect_to_plex(self):
        """Establish connection to Plex server using credentials."""
        try:
            plex_creds = self.credentials.get('plex', {})
            plex_url = plex_creds.get('plex_url') or plex_creds.get('url')
            plex_token = plex_creds.get('plex_token') or plex_creds.get('token')

            if not plex_url or not plex_token:
                raise ValueError("Plex URL or token not found in credentials")

            self.logger.info(f"Connecting to Plex server at {plex_url}")
            return PlexServer(plex_url, plex_token)
        except Exception as e:
            self.logger.error(f"Failed to connect to Plex: {str(e)}")
            raise

    def search_music(self, query, libtype='artist'):
        """Search for music in Plex library."""
        try:
            music = self.server.library.section('Music')
            return music.search(query, libtype=libtype)
        except Exception as e:
            self.logger.error(f"Error searching for {libtype} '{query}': {str(e)}")
            return []

    def get_playlist(self, playlist_name):
        """Get a playlist by name."""
        try:
            playlists = self.server.playlists()
            return next((p for p in playlists if p.title.lower() == playlist_name.lower()), None)
        except Exception as e:
            self.logger.error(f"Error getting playlist '{playlist_name}': {str(e)}")
            return None

    def download_track(self, track, save_path, keep_original_name=False):
        """Download a track to the specified path."""
        try:
            track.download(save_path, keep_original_name=keep_original_name)
        except Exception as e:
            self.logger.error(f"Error downloading track '{track.title}': {str(e)}")
            raise

    def download_album_cover(self, album, save_path):
        """Download album cover to the specified path."""
        try:
            with open(save_path, 'wb') as f:
                f.write(album.thumb.download())
        except Exception as e:
            self.logger.error(f"Error downloading cover for album '{album.title}': {str(e)}")
            raise

    def get_artist_albums(self, artist):
        """Get all albums for an artist."""
        try:
            return artist.albums()
        except Exception as e:
            self.logger.error(f"Error getting albums for artist '{artist.title}': {str(e)}")
            return []

    def get_album_tracks(self, album):
        """Get all tracks in an album."""
        try:
            return album.tracks()
        except Exception as e:
            self.logger.error(f"Error getting tracks for album '{album.title}': {str(e)}")
            return []