# utils/logger.py
import logging
from pathlib import Path

class SingletonLogger:
    _instance = None

    @classmethod
    def get_logger(cls, log_file='logs/app.log'):
        if cls._instance is None:
            cls._instance = cls._setup_logger(log_file)
        return cls._instance

    @staticmethod
    def _setup_logger(log_file):
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger('MusicOrganizer')
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(logging.DEBUG)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger
    
def log_with_exception(logger, level, message, exception=None):
    if exception:
        logger.exception(f"{message}: {str(exception)}")
    else:
        logger.log(level, message)