import os
from pathlib import Path

class Config:
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/app/uploads')
    CONVERTED_FOLDER = os.getenv('CONVERTED_FOLDER', '/app/converted')
    LOGS_FOLDER = os.getenv('LOGS_FOLDER', '/app/logs')

    # File limits
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50)) * 1024 * 1024
    MAX_DOWNLOAD_SIZE = int(os.getenv('MAX_DOWNLOAD_SIZE', 100)) * 1024 * 1024

    # Background tasks
    CLEANUP_INTERVAL = int(os.getenv('CLEANUP_INTERVAL', 3600))
    FILE_TTL = int(os.getenv('FILE_TTL', 3600))

    # Supported formats
    SUPPORTED_CONVERSIONS = {
        'document': {
            'from': ['.docx', '.doc', '.odt', '.rtf', '.txt'],
            'to': ['.pdf', '.docx', '.txt', '.html']
        },
        'image': {
            'from': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'to': ['.jpg', '.png', '.pdf', '.webp']
        },
        'video': {
            'from': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'],
            'to': ['.mp4', '.avi', '.gif']
        },
        'audio': {
            'from': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
            'to': ['.mp3', '.wav', '.ogg']
        }
    }

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.CONVERTED_FOLDER, exist_ok=True)
        os.makedirs(Config.LOGS_FOLDER, exist_ok=True)
