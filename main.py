# main.py

import sys
import traceback
from utils import SingletonLogger, ConfigReader, CredentialHandler
from clients.music_clients.music_clients import MusicClient

def main():
    logger = SingletonLogger.get_logger()
    logger.info("Application started")

    try:
        # Read configuration
        config_reader = ConfigReader()
        config = config_reader.read_config()
        logger.info("Configuration loaded successfully")

        # Get credentials
        credential_handler = CredentialHandler()
        credentials = credential_handler.get_credentials()
        logger.info("Credentials loaded successfully")

        # Initialize MusicClient
        music_client = MusicClient()
        logger.info("MusicClient initialized")

        # Process music
        music_client.process_music()
        logger.info("Music processing completed")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

    logger.info("Application finished successfully")

if __name__ == "__main__":
    main()