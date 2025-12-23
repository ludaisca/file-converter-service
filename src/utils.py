"""
Funciones utilidad para el servicio de conversión.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
import requests
from functools import wraps
import gzip
import io

from src.config import settings
from src.logging import logger


def cleanup_files(days_old: int = 7) -> int:
    deleted_count = 0
    cutoff_time = datetime.now() - timedelta(days=days_old)
    
    if settings.UPLOAD_FOLDER.exists():
        deleted_count += _cleanup_directory(
            settings.UPLOAD_FOLDER,
            cutoff_time
        )
    
    if settings.CONVERTED_FOLDER.exists():
        deleted_count += _cleanup_directory(
            settings.CONVERTED_FOLDER,
            cutoff_time
        )
    
    if settings.TEMP_FOLDER.exists():
        deleted_count += _cleanup_directory(
            settings.TEMP_FOLDER,
            cutoff_time
        )
    
    logger.info(f"Cleanup completed: {deleted_count} files deleted")
    return deleted_count


def _cleanup_directory(directory: Path, cutoff_time: datetime) -> int:
    deleted_count = 0
    
    try:
        for file_path in directory.iterdir():
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {file_path}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error cleaning directory {directory}: {str(e)}")
    
    return deleted_count


def get_file_size(file_path: Path) -> float:
    if file_path.exists():
        return file_path.stat().st_size / (1024 * 1024)
    return 0.0


def get_allowed_extensions() -> List[str]:
    return [ext.lower() for ext in settings.ALLOWED_EXTENSIONS]


def is_allowed_extension(filename: str) -> bool:
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in get_allowed_extensions()


def get_file_extension(filename: str) -> str:
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def sanitize_filename(filename: str) -> str:
    import re
    
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename.lstrip('.')
    
    return filename or 'file'


def ensure_upload_folder_exists() -> Path:
    settings.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    return settings.UPLOAD_FOLDER


def ensure_converted_folder_exists() -> Path:
    settings.CONVERTED_FOLDER.mkdir(parents=True, exist_ok=True)
    return settings.CONVERTED_FOLDER


def download_file_from_url(url: str, destination_folder: Path) -> Path:
    import uuid
    
    try:
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL scheme: {url}")
        
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        content_disposition = response.headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[-1].strip('\'"')
        else:
            filename = url.split('/')[-1] or 'downloaded_file'
        
        filename = sanitize_filename(filename)
        
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = destination_folder / unique_name
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise ValueError(f"Downloaded file is empty: {url}")
        
        logger.info(f"File downloaded successfully from {url}: {unique_name}")
        return file_path
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file from {url}: {str(e)}")
        raise ValueError(f"Failed to download file: {str(e)}")
    
    except Exception as e:
        logger.error(f"Unexpected error downloading file: {str(e)}")
        raise ValueError(f"Error downloading file: {str(e)}")


def gzip_response(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        from flask import request, make_response
        
        response = make_response(f(*args, **kwargs))
        
        if 'gzip' not in request.headers.get('Accept-Encoding', ''):
            return response
        
        if response.data:
            gzip_buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as gzip_file:
                gzip_file.write(response.data)
            
            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response.data)
        
        return response
    
    return wrapper
