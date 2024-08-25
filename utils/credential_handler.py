# utils/credential_handler.py
import tomli
from pathlib import Path

class CredentialHandler:
    def __init__(self, credentials_path='config/credentials.toml'):
        self.credentials_path = Path(credentials_path)

    def get_credentials(self):
        try:
            with open(self.credentials_path, 'rb') as f:
                return tomli.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
        except tomli.TOMLDecodeError as e:
            raise ValueError(f"Error parsing credentials file: {e}")

    def get_service_credentials(self, service):
        credentials = self.get_credentials()
        if service not in credentials:
            raise KeyError(f"Credentials for service '{service}' not found")
        return credentials[service]