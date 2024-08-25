# clients/music_clients/music_clients.py

from utils import SingletonLogger, ConfigReader, CredentialHandler
from ..service_clients.service_clients import ServiceClients
from ._music_downloader import MusicDownloader
from ._duplicate_finder import DuplicateFinder
from ._duplicate_deletion import DuplicateDeletion
from ._empty_deletion import EmptyDeletion
from ._loudness_data_analyzer import LoudnessDataAnalyzer
from ._metadata_setter import MetadataSetter

class MusicClient:
    def __init__(self):
        self.logger = SingletonLogger.get_logger()
        self.logger.info("Initializing Music Client...")
        
        config_reader = ConfigReader()
        self.config = config_reader.read_config()
        self._log_config_details()
        
        credential_handler = CredentialHandler()
        self.credentials = credential_handler.get_credentials()
        self.logger.info("Credentials loaded successfully")
        
        self.service_clients = ServiceClients()
        
        self.music_downloader = MusicDownloader(self.service_clients, self.config, self.logger)
        self.duplicate_finder = DuplicateFinder(self.config)
        self.duplicate_deletion = DuplicateDeletion(self.config)
        self.empty_deletion = EmptyDeletion(self.config)
        self.loudness_analyzer = LoudnessDataAnalyzer(self.config)
        self.metadata_setter = MetadataSetter(self.config)

    def _log_config_details(self):
        self.logger.info("Configuration details:")
        self.logger.info(f"Music library path: {self.config['directories']['music_library']}")
        self.logger.info(f"Music download enabled: {self.config['music-download'].get('music-download', False)}")
        if self.config['music-download'].get('music-download', False):
            self.logger.info(f"Download type: {self.config['music-download']['download-object']}")
            self.logger.info(f"Download mode: {self.config['music-download']['download-mode']}")
            self.logger.info(f"Download client: {self.config['music-download']['download-client']}")
        
        # Log other relevant configuration details
        if 'duplicate_deletion' in self.config:
            self.logger.info(f"Duplicate deletion enabled: {self.config['duplicate_deletion'].get('enabled', False)}")
        if 'empty_deletion' in self.config:
            self.logger.info(f"Empty folder deletion enabled: {self.config['empty_deletion'].get('enabled', False)}")
        if 'loudness_analysis' in self.config:
            self.logger.info(f"Loudness analysis enabled: {self.config['loudness_analysis'].get('enabled', False)}")
        if 'metadata_setting' in self.config:
            self.logger.info(f"Metadata setting enabled: {self.config['metadata_setting'].get('enabled', False)}")

    def process_music(self):
        try:
            self.logger.info("Starting music processing...")
            
            # Download music
            if self.config['music-download'].get('music-download', False):
                download_type = self.config['music-download']['download-object']
                targets = self._get_targets(download_type)
                self.logger.info(f"Downloading music. Type: {download_type}, Targets: {targets}")
                self.music_downloader.download_music(download_type, targets)
            else:
                self.logger.info("Music download is disabled in config. Skipping download process.")
            
            # Other processing steps
            if self.config.get('duplicate_deletion', {}).get('enabled', False):
                self.logger.info("Starting duplicate detection and deletion...")
                self.duplicate_finder.find_duplicates()
                self.duplicate_deletion.delete_duplicates()
            
            if self.config.get('empty_deletion', {}).get('enabled', False):
                self.logger.info("Starting empty folder deletion...")
                self.empty_deletion.delete_empty_folders()
            
            if self.config.get('loudness_analysis', {}).get('enabled', False):
                self.logger.info("Starting loudness analysis...")
                self.loudness_analyzer.analyze_loudness()
            
            if self.config.get('metadata_setting', {}).get('enabled', False):
                self.logger.info("Starting metadata setting...")
                self.metadata_setter.set_metadata()
            
            self.logger.info("Music processing completed successfully.")
        except Exception as e:
            self.logger.error(f"An error occurred during music processing: {str(e)}")

    def _get_targets(self, download_type):
        """Read targets from the appropriate file based on download type."""
        file_path = f'targets/{"artists" if download_type == "artist" else "playlists"}.txt'
        try:
            with open(file_path, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
            self.logger.info(f"Read {len(targets)} targets from {file_path}")
            return targets
        except Exception as e:
            self.logger.error(f"Error reading targets from {file_path}: {str(e)}")
            return []