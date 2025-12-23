import os
from pathlib import Path

class Config:
    """Configuración global de la aplicación.
    
    Soporta conversión de:
    - Documentos: Word, Excel, PowerPoint, PDF, Texto, CSV, JSON, XML
    - Imágenes: JPG, PNG, GIF, BMP, TIFF, WebP, SVG, HEIC, AVIF
    - Audio: MP3, WAV, OGG, M4A, FLAC, AAC, OPUS, WMA
    - Video: MP4, AVI, MOV, MKV, FLV, WMV, WebM, 3GP
    - Archivos: ZIP, 7Z, RAR, TAR, GZIP, BZIP2
    """
    
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

    # Supported formats - v2.1.0 (Comprehensive Support)
    SUPPORTED_CONVERSIONS = {
        'documents': {
            'from': ['.docx', '.doc', '.odt', '.rtf', '.txt', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.json', '.xml'],
            'to': ['.pdf', '.docx', '.doc', '.txt', '.html', '.odt', '.rtf', '.csv', '.json', '.xml']
        },
        'spreadsheets': {
            'from': ['.xlsx', '.xls', '.csv', '.ods'],
            'to': ['.xlsx', '.xls', '.csv', '.pdf', '.json', '.xml']
        },
        'presentations': {
            'from': ['.pptx', '.ppt', '.odp'],
            'to': ['.pptx', '.ppt', '.pdf', '.html']
        },
        'images': {
            'from': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.heic', '.avif', '.ico', '.psd', '.xcf'],
            'to': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.ico', '.pdf', '.svg']
        },
        'audio': {
            'from': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.opus', '.wma', '.aiff', '.ape'],
            'to': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.opus', '.wma', '.aiff']
        },
        'video': {
            'from': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.3gp', '.f4v', '.m2ts'],
            'to': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif', '.webp', '.3gp']
        },
        'archives': {
            'from': ['.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.xz'],
            'to': ['.zip', '.7z', '.tar', '.tar.gz']
        },
        'web': {
            'from': ['.html', '.htm', '.css', '.js'],
            'to': ['.html', '.htm', '.pdf']
        }
    }

    # All supported formats (flat list for validation)
    ALL_INPUT_FORMATS = set()
    ALL_OUTPUT_FORMATS = set()
    
    @classmethod
    def _init_formats(cls):
        """Inicializar lista de todos los formatos."""
        for category in cls.SUPPORTED_CONVERSIONS.values():
            cls.ALL_INPUT_FORMATS.update(category.get('from', []))
            cls.ALL_OUTPUT_FORMATS.update(category.get('to', []))
    
    @staticmethod
    def init_app(app):
        """Inicializar aplicación."""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.CONVERTED_FOLDER, exist_ok=True)
        os.makedirs(Config.LOGS_FOLDER, exist_ok=True)
        
        # Inicializar formatos
        Config._init_formats()


# Inicializar formatos al cargar el módulo
Config._init_formats()
