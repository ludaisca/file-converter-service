from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path
from typing import List
import os

class Settings(BaseSettings):
    DEBUG: bool = Field(default=False)
    ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=5000)
    WORKERS: int = Field(default=4)
    UPLOAD_FOLDER: Path = Field(default="/tmp/file-converter/uploads")
    CONVERTED_FOLDER: Path = Field(default="/tmp/file-converter/converted")
    LOGS_FOLDER: Path = Field(default="/tmp/file-converter/logs")
    TEMP_FOLDER: Path = Field(default="/tmp/file-converter/temp")
    MAX_FILE_SIZE: int = Field(default=500 * 1024 * 1024)
    ALLOWED_EXTENSIONS: List[str] = Field(default=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'json', 'xml', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'avi', 'mov', 'mkv'])
    ENABLE_OCR: bool = Field(default=True)
    OCR_DEFAULT_LANGUAGE: str = Field(default="spa")
    OCR_MAX_PAGES: int = Field(default=50)
    OCR_TIMEOUT_SECONDS: int = Field(default=300)
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW: int = Field(default=60)
    ENABLE_CACHE: bool = Field(default=False)
    CACHE_TYPE: str = Field(default="simple")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CACHE_TTL_HOURS: int = Field(default=24)
    CORS_ORIGINS: List[str] = Field(default=["*"])
    MAX_UPLOAD_TIMEOUT: int = Field(default=600)
    
    SUPPORTED_CONVERSIONS: dict = Field(default={
        'documents': {'from': ['.docx', '.doc', '.odt', '.rtf', '.txt', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.json', '.xml'], 'to': ['.pdf', '.docx', '.doc', '.txt', '.html', '.odt', '.rtf', '.csv', '.json', '.xml']},
        'spreadsheets': {'from': ['.xlsx', '.xls', '.csv', '.ods'], 'to': ['.xlsx', '.xls', '.csv', '.pdf', '.json', '.xml']},
        'presentations': {'from': ['.pptx', '.ppt', '.odp'], 'to': ['.pptx', '.ppt', '.pdf', '.html']},
        'images': {'from': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.heic', '.avif', '.ico', '.psd', '.xcf'], 'to': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.ico', '.pdf', '.svg']},
        'audio': {'from': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.opus', '.wma', '.aiff', '.ape'], 'to': ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.opus', '.wma', '.aiff']},
        'video': {'from': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.3gp', '.f4v', '.m2ts'], 'to': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif', '.webp', '.3gp']},
        'archives': {'from': ['.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.xz'], 'to': ['.zip', '.7z', '.tar', '.tar.gz']},
        'web': {'from': ['.html', '.htm', '.css', '.js'], 'to': ['.html', '.htm', '.pdf']}
    })

    @field_validator('UPLOAD_FOLDER', 'CONVERTED_FOLDER', 'LOGS_FOLDER', 'TEMP_FOLDER', mode='before')
    @classmethod
    def create_directories(cls, v):
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @field_validator('ENV')
    @classmethod
    def validate_env(cls, v):
        valid_envs = ['development', 'production', 'testing']
        if v not in valid_envs:
            raise ValueError(f'ENV must be one of {valid_envs}')
        return v

    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()

    @field_validator('MAX_FILE_SIZE')
    @classmethod
    def validate_max_file_size(cls, v):
        min_size = 1 * 1024 * 1024
        max_size = 10 * 1024 * 1024 * 1024
        if not (min_size <= v <= max_size):
            raise ValueError(f'MAX_FILE_SIZE must be between {min_size} and {max_size} bytes')
        return v

    @field_validator('OCR_MAX_PAGES')
    @classmethod
    def validate_ocr_max_pages(cls, v):
        if v <= 0:
            raise ValueError('OCR_MAX_PAGES must be greater than 0')
        if v > 1000:
            raise ValueError('OCR_MAX_PAGES must be less than 1000')
        return v

    @field_validator('RATE_LIMIT_REQUESTS', 'RATE_LIMIT_WINDOW')
    @classmethod
    def validate_rate_limit(cls, v):
        if v <= 0:
            raise ValueError('Rate limit values must be greater than 0')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

class Config:
    SUPPORTED_CONVERSIONS = settings.SUPPORTED_CONVERSIONS
    UPLOAD_FOLDER = settings.UPLOAD_FOLDER
    CONVERTED_FOLDER = settings.CONVERTED_FOLDER
    LOGS_FOLDER = settings.LOGS_FOLDER

def get_settings() -> Settings:
    return settings

def validate_settings() -> bool:
    from .exceptions import InvalidConfigException
    try:
        assert settings.UPLOAD_FOLDER.exists()
        assert settings.CONVERTED_FOLDER.exists()
        assert settings.LOGS_FOLDER.exists()
        assert os.access(settings.UPLOAD_FOLDER, os.W_OK)
        assert os.access(settings.CONVERTED_FOLDER, os.W_OK)
        assert os.access(settings.LOGS_FOLDER, os.W_OK)
        return True
    except AssertionError as e:
        raise InvalidConfigException(str(e))

if settings.ENV == "production":
    settings.DEBUG = False
    settings.LOG_LEVEL = "WARNING"
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    if cors_origins_env:
        settings.CORS_ORIGINS = cors_origins_env.split(",")
elif settings.ENV == "testing":
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    settings.ENABLE_CACHE = False
    settings.RATE_LIMIT_ENABLED = False
