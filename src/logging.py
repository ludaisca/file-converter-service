import logging
import os
from .config import Config

def setup_logging():
    log_file_path = os.path.join(Config.LOGS_FOLDER, 'app.log')

    # Ensure the directory exists (Config.init_app handles it, but good to be safe)
    os.makedirs(Config.LOGS_FOLDER, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path, mode='a')
        ]
    )
    return logging.getLogger('file_converter')

logger = setup_logging()
