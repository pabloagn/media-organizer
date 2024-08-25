# clients/service_clients/google_images_client.py

import requests
from utils import SingletonLogger, ConfigReader, CredentialHandler

class GoogleImagesClient:
    def __init__(self):
        self.logger = SingletonLogger.get_logger()
        self.config = ConfigReader().read_config()
        self.credentials = CredentialHandler().get_service_credentials('google_images')
        self.search_engine_id = self.credentials['search_engine_id']
        self.api_key = self.credentials['api_key']

    def search_images(self, query, num_results=10):
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'cx': self.search_engine_id,
                'key': self.api_key,
                'searchType': 'image',
                'num': num_results
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()['items']
        except Exception as e:
            self.logger.error(f"Google Images search error for query '{query}': {str(e)}")
            raise

    def download_image(self, image_url, save_path):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return save_path
        except Exception as e:
            self.logger.error(f"Error downloading image from '{image_url}': {str(e)}")
            raise

    # Add more methods as needed