import os
import uuid
import requests
import gzip
import time
import shutil
from pathlib import Path
from functools import wraps
from werkzeug.utils import secure_filename
from flask import request
from .logging import logger
from .config import Config

def gzip_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        rv = f(*args, **kwargs)
        if isinstance(rv, tuple):
            response_data, status_code = rv[0], rv[1]
        else:
            response_data = rv
            status_code = 200

        if request.accept_encodings.get('gzip'):
            if isinstance(response_data, str):
                compressed = gzip.compress(response_data.encode('utf-8'))
                return compressed, status_code, {'Content-Encoding': 'gzip', 'Content-Type': 'application/json'}

        return rv
    return decorated_function

def download_file_from_url(url: str, upload_folder: Path) -> Path:
    logger.info(f"Downloading file from URL: {url}")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        original_name = url.split('/')[-1] or 'downloaded_file'
        name, ext = os.path.splitext(original_name)

        safe_name = secure_filename(name) or 'file'
        unique_name = f"{uuid.uuid4().hex}_{safe_name}{ext}"
        file_path = upload_folder / unique_name

        size = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    size += len(chunk)
                    if size > Config.MAX_DOWNLOAD_SIZE:
                        file_path.unlink()
                        logger.error(f"Downloaded file exceeds maximum size")
                        raise ValueError(f'Downloaded file exceeds maximum size of {Config.MAX_DOWNLOAD_SIZE / (1024*1024):.0f}MB')
                    f.write(chunk)

        logger.info(f"Successfully downloaded file: {unique_name} ({size} bytes)")
        return file_path
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file from URL: {str(e)}")
        raise ValueError(f'Error downloading file from URL: {str(e)}')
    except Exception as e:
        logger.error(f"Error processing downloaded file: {str(e)}")
        raise ValueError(f'Error processing downloaded file: {str(e)}')

def cleanup_files():
    """Background task to clean up old files."""
    logger.info("Starting cleanup thread...")
    while True:
        try:
            now = time.time()
            for folder in [Config.UPLOAD_FOLDER, Config.CONVERTED_FOLDER]:
                if not os.path.exists(folder):
                    continue
                for f in os.listdir(folder):
                    f_path = os.path.join(folder, f)
                    try:
                        if os.path.isfile(f_path):
                            if os.stat(f_path).st_mtime < now - Config.FILE_TTL:
                                os.remove(f_path)
                                logger.debug(f"Deleted old file: {f}")
                    except Exception as e:
                        logger.debug(f"Error processing {f_path}: {e}")
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")
        time.sleep(Config.CLEANUP_INTERVAL)
