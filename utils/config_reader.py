# utils/config_reader.py
import tomli
from pathlib import Path

class ConfigReader:
    def __init__(self, config_path='config/config.toml'):
        self.config_path = Path(config_path)

    def read_config(self):
        try:
            with open(self.config_path, 'rb') as f:
                return tomli.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except tomli.TOMLDecodeError as e:
            raise ValueError(f"Error parsing config file: {e}")