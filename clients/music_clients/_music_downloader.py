# clients/music_clients/_music_downloader.py

import os
from utils.logger import SingletonLogger

class MusicDownloader:
    def __init__(self, service_clients, config, logger=None):
        self.service_clients = service_clients
        self.config = config
        self.logger = logger or SingletonLogger.get_logger()
        self.music_library_path = self.config['directories']['music_library']

    def download_music(self, download_type, targets):
        """
        Main method to orchestrate music downloading based on config.
        
        :param download_type: Either 'artist' or 'playlist'
        :param targets: List of artists or playlists to download
        """
        try:
            if download_type == 'artist':
                self._download_artists(targets)
            elif download_type == 'playlist':
                self._download_playlists(targets)
            else:
                self.logger.error(f"Unsupported download type: {download_type}")
        except Exception as e:
            self.logger.error(f"An error occurred during music download: {str(e)}")

    def _download_artists(self, artists):
        """Download music for all specified artists."""
        for artist in artists:
            try:
                self._download_artist(artist)
            except Exception as e:
                self.logger.error(f"Failed to download artist {artist}: {str(e)}")

    def _download_playlists(self, playlists):
        """Download music for all specified playlists."""
        for playlist in playlists:
            try:
                self._download_playlist(playlist)
            except Exception as e:
                self.logger.error(f"Failed to download playlist {playlist}: {str(e)}")

    def _download_artist(self, artist_name):
        """Download all music for a given artist."""
        try:
            artists = self.service_clients.search_music(artist_name, 'artist')
            if not artists:
                self.logger.warning(f"No artists found for: {artist_name}")
                return

            for artist in artists:
                if artist_name.lower() in artist.title.lower():
                    for album in artist.albums():
                        self._download_album(album)

            self.logger.info(f"Finished downloading music for artist: {artist_name}")
        except Exception as e:
            self.logger.error(f"Error downloading artist {artist_name}: {str(e)}")

    def _download_playlist(self, playlist_name):
        """Download all music for a given playlist and create m3u8 file."""
        try:
            playlist = self.service_clients.get_playlist(playlist_name)
            if not playlist:
                self.logger.warning(f"No playlist found with name: {playlist_name}")
                return

            m3u8_content = "#EXTM3U\n"
            metadata_path = os.path.join(self.music_library_path, 'Metadata', 'Playlists')
            os.makedirs(metadata_path, exist_ok=True)

            for item in playlist.items():
                track_path = self._download_track(item)
                if track_path:
                    relative_path = os.path.relpath(track_path, self.music_library_path)
                    m3u8_content += f"#EXTINF:{int(item.duration/1000)},{item.grandparentTitle} - {item.title}\n{relative_path}\n"

            m3u8_path = os.path.join(metadata_path, f"{playlist_name}.m3u8")
            with open(m3u8_path, 'w', encoding='utf-8') as f:
                f.write(m3u8_content)
            self.logger.info(f"Created playlist file: {m3u8_path}")
        except Exception as e:
            self.logger.error(f"Error downloading playlist {playlist_name}: {str(e)}")

    def _download_album(self, album):
        """Download all tracks in an album and its cover."""
        try:
            album_path = os.path.join(self.music_library_path, 'Library', self._sanitize_filename(album.parentTitle), 
                                      self._sanitize_filename(f"{album.title} [{album.year}]"))
            os.makedirs(album_path, exist_ok=True)

            for track in album.tracks():
                self._download_track(track, album_path)

            self._download_album_cover(album, album_path)
        except Exception as e:
            self.logger.error(f"Error downloading album {album.title}: {str(e)}")

    def _download_track(self, track, album_path=None):
        """Download a single track."""
        try:
            if album_path is None:
                album_path = os.path.join(self.music_library_path, 'Library', self._sanitize_filename(track.grandparentTitle), 
                                          self._sanitize_filename(f"{track.parentTitle} [{track.album().year}]"))
                os.makedirs(album_path, exist_ok=True)

            track_filename = self._sanitize_filename(f"{track.trackNumber:02d} - {track.grandparentTitle} - {track.title}.{track.media[0].parts[0].file.split('.')[-1]}")
            track_path = os.path.join(album_path, track_filename)

            if os.path.exists(track_path):
                self.logger.info(f"Track already exists: {track_path}")
            else:
                self.service_clients.download_track(track, album_path, keep_original_name=False)
                self.logger.info(f"Downloaded: {track_path}")

            return track_path
        except Exception as e:
            self.logger.error(f"Error downloading track {track.title}: {str(e)}")
            return None

    def _download_album_cover(self, album, album_path):
        """Download the album cover."""
        try:
            cover_path = os.path.join(album_path, "Cover.jpg")
            if not os.path.exists(cover_path):
                self.service_clients.download_album_cover(album, cover_path)
                self.logger.info(f"Downloaded album cover: {cover_path}")
        except Exception as e:
            self.logger.error(f"Failed to download album cover for {album.title}: {str(e)}")

    @staticmethod
    def _sanitize_filename(filename):
        """Remove invalid characters from filename."""
        return ''.join(char for char in filename if char.isalnum() or char in (' ', '.', '_', '-'))