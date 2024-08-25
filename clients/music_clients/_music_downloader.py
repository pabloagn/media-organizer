# clients/music_clients/_music_downloader.py

import os
from utils.logger import SingletonLogger

class MusicDownloader:
    def __init__(self, service_clients, config, logger=None):
        self.service_clients = service_clients
        self.config = config
        self.logger = logger or SingletonLogger.get_logger()
        self.music_root = self.config['directories']['music_root'].replace('\\', '/')
        self.music_library = self.config['directories']['music_library'].replace('\\', '/')
        self.artwork_directory = self.config['directories']['artwork_directory'].replace('\\', '/')
        self.playlists_directory = self.config['directories']['playlists_directory'].replace('\\', '/')

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
        """Download all music for a given artist and the artist image."""
        try:
            artists = self.service_clients.search_music(artist_name, 'artist')
            if not artists:
                self.logger.warning(f"No artists found for: {artist_name}")
                return

            for artist in artists:
                if artist_name.lower() in artist.title.lower():
                    self._download_artist_image(artist)
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
            os.makedirs(self.playlists_directory, exist_ok=True)

            for item in playlist.items():
                track_path = self._download_track(item)
                if track_path:
                    m3u8_content += f"#EXTINF:{int(item.duration/1000)},{item.grandparentTitle} - {item.title}\n{track_path}\n"
                
                # Download artist image after downloading the track
                self._download_artist_image(item.grandparentTitle)

            m3u8_path = os.path.join(self.playlists_directory, f"{playlist_name}.m3u8").replace('\\', '/')
            with open(m3u8_path, 'w', encoding='utf-8') as f:
                f.write(m3u8_content)
            self.logger.info(f"Created playlist file: {m3u8_path}")
        except Exception as e:
            self.logger.error(f"Error downloading playlist {playlist_name}: {str(e)}")

    def _download_album(self, album):
        """Download all tracks in an album and its cover."""
        try:
            album_path = self._get_album_path(album)
            os.makedirs(album_path, exist_ok=True)

            for track in album.tracks():
                self._download_track(track, album_path)

            self._download_album_cover(album, album_path)
        except Exception as e:
            self.logger.error(f"Error downloading album {album.title}: {str(e)}")

    def _download_track(self, track, album_path=None):
        """Download a single track using the original filename from Plex."""
        try:
            self.logger.debug(f"Attempting to download track: {track.title}")
            if album_path is None:
                album_path = self._get_album_path(track.album())
            self.logger.debug(f"Album path: {album_path}")

            # Use the original filename from Plex
            original_filename = os.path.basename(track.media[0].parts[0].file)
            self.logger.debug(f"Original filename: {original_filename}")
            track_path = os.path.join(album_path, original_filename).replace('\\', '/')
            self.logger.debug(f"Full track path: {track_path}")

            if os.path.exists(track_path):
                self.logger.info(f"Track already exists: {track_path}")
            else:
                self.logger.debug("Calling service_clients.download_track")
                success = self.service_clients.download_track(track, album_path, keep_original_name=True)
                if success:
                    self.logger.info(f"Downloaded: {track_path}")
                else:
                    self.logger.error(f"Failed to download: {track_path}")

            return track_path
        except Exception as e:
            self.logger.error(f"Error downloading track {track.title}: {str(e)}")
            return None

    def _download_album_cover(self, album, album_path):
        """Download the album cover."""
        try:
            cover_path = os.path.join(album_path, "cover.jpg").replace('\\', '/')
            if not os.path.exists(cover_path):
                self.service_clients.download_album_cover(album, cover_path)
                self.logger.info(f"Downloaded album cover: {cover_path}")
            else:
                self.logger.info(f"Album cover already exists: {cover_path}")
        except Exception as e:
            self.logger.error(f"Failed to download album cover for {album.title}: {str(e)}")

    def _download_artist_image(self, artist_name):
        """Download the artist image."""
        try:
            self.logger.debug(f"Attempting to download image for artist: {artist_name}")
            artists = self.service_clients.search_music(artist_name, 'artist')
            if not artists:
                self.logger.warning(f"No artists found for: {artist_name}")
                return

            for artist in artists:
                if artist_name.lower() in artist.title.lower():
                    artist_path = os.path.join(self.artwork_directory, artist.title).replace('\\', '/')
                    os.makedirs(artist_path, exist_ok=True)
                    cover_path = os.path.join(artist_path, "cover.jpg").replace('\\', '/')
                    self.logger.debug(f"Artist image path: {cover_path}")
                    if not os.path.exists(cover_path):
                        success = self.service_clients.download_artist_image(artist, cover_path)
                        if success:
                            self.logger.info(f"Downloaded artist image: {cover_path}")
                        else:
                            self.logger.warning(f"Failed to download artist image for {artist.title}")
                    else:
                        self.logger.info(f"Artist image already exists: {cover_path}")
                    break  # We only need to download for the first matching artist
        except Exception as e:
            self.logger.error(f"Error downloading artist image for {artist_name}: {str(e)}")

    def _get_album_path(self, album):
        """Get the correct album path based on Plex metadata."""
        try:
            # Get the full file path of the first track in the album
            first_track = album.tracks()[0]
            full_path = first_track.media[0].parts[0].file.replace('\\', '/')
            
            # Remove the prefix '/share/NFSv=4/Media/Music/Album'
            relative_path = full_path.split('/Album/')[-1]
            
            # Split the path to get artist and album name
            path_parts = relative_path.split('/')
            artist_name = path_parts[0]
            album_name = path_parts[1]
            
            # Construct the full album path
            return os.path.join(self.music_library, artist_name, album_name).replace('\\', '/')
        except Exception as e:
            self.logger.error(f"Error getting album path for {album.title}: {str(e)}")
            # Fallback to a basic path if there's an error
            return os.path.join(self.music_library, album.parentTitle, album.title).replace('\\', '/')

    @staticmethod
    def _sanitize_filename(filename):
        """Remove invalid characters from filename."""
        return ''.join(char for char in filename if char.isalnum() or char in (' ', '.', '_', '-', '&', '\'', '(', ')'))