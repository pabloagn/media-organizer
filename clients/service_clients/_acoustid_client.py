# clients/service_clients/acoustid_client.py

import acoustid
from utils import SingletonLogger, ConfigReader, CredentialHandler

class AcoustIDClient:
    def __init__(self):
        self.logger = SingletonLogger.get_logger()
        self.config = ConfigReader().read_config()
        self.credentials = CredentialHandler().get_service_credentials('acoustid')
        self.api_key = self.credentials['api_key']

    def fingerprint_file(self, file_path):
        try:
            duration, fingerprint = acoustid.fingerprint_file(file_path)
            return duration, fingerprint
        except acoustid.FingerprintGenerationError as e:
            self.logger.error(f"Error generating fingerprint for '{file_path}': {str(e)}")
            raise

    def lookup(self, fingerprint, duration):
        try:
            results = acoustid.lookup(self.api_key, fingerprint, duration)
            return results
        except acoustid.WebServiceError as e:
            self.logger.error(f"AcoustID lookup error: {str(e)}")
            raise

    def identify_file(self, file_path):
        try:
            results = acoustid.match(self.api_key, file_path)
            return results
        except acoustid.FingerprintGenerationError as e:
            self.logger.error(f"Error identifying file '{file_path}': {str(e)}")
            raise

    # Add more methods as needed