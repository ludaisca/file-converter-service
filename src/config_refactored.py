"""
Configuración refactorizada usando Pydantic.
Valida automáticamente variables de entorno y proporciona valores por defecto seguros.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path
from typing import List
import os


class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación.
    
    Variables:
        - Se cargan desde .env usando python-dotenv
        - Se validan automáticamente con Pydantic
        - Incluyen valores por defecto seguros
        - Soportan validadores personalizados
    """
    
    # ==================
    # Configuración General
    # ==================
    DEBUG: bool = Field(default=False, description="Modo debug")
    ENV: str = Field(default="development", description="Entorno (development/production/testing)")
    LOG_LEVEL: str = Field(default="INFO", description="Nivel de logging")
    
    # ==================
    # Servidor
    # ==================
    HOST: str = Field(default="0.0.0.0", description="Host del servidor")
    PORT: int = Field(default=5000, description="Puerto del servidor")
    WORKERS: int = Field(default=4, description="Número de workers (Gunicorn)")
    
    # ==================
    # Rutas de Archivos
    # ==================
    UPLOAD_FOLDER: Path = Field(
        default="/tmp/file-converter/uploads",
        description="Carpeta para archivos subidos"
    )
    CONVERTED_FOLDER: Path = Field(
        default="/tmp/file-converter/converted",
        description="Carpeta para archivos convertidos"
    )
    LOGS_FOLDER: Path = Field(
        default="/tmp/file-converter/logs",
        description="Carpeta para logs"
    )
    TEMP_FOLDER: Path = Field(
        default="/tmp/file-converter/temp",
        description="Carpeta temporal para procesamiento"
    )
    
    # ==================
    # Límites de Archivos
    # ==================
    MAX_FILE_SIZE: int = Field(
        default=500 * 1024 * 1024,  # 500MB
        description="Tamaño máximo de archivo en bytes"
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'txt', 'csv', 'json', 'xml',
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
            'mp4', 'avi', 'mov', 'mkv'
        ],
        description="Extensiones permitidas"
    )
    
    # ==================
    # Configuración OCR
    # ==================
    ENABLE_OCR: bool = Field(
        default=True,
        description="Habilitar funcionalidad OCR"
    )
    OCR_DEFAULT_LANGUAGE: str = Field(
        default="spa",
        description="Idioma por defecto para OCR"
    )
    OCR_MAX_PAGES: int = Field(
        default=50,
        description="Máximo número de páginas a procesar en OCR"
    )
    OCR_TIMEOUT_SECONDS: int = Field(
        default=300,
        description="Timeout para operaciones OCR en segundos"
    )
    
    # ==================
    # Rate Limiting
    # ==================
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Habilitar rate limiting"
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description="Número de requests permitidos en la ventana"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=60,
        description="Ventana de tiempo en segundos para rate limiting"
    )
    
    # ==================
    # Caché
    # ==================
    ENABLE_CACHE: bool = Field(
        default=False,
        description="Habilitar caché"
    )
    CACHE_TYPE: str = Field(
        default="simple",
        description="Tipo de caché (simple/redis)"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexión a Redis"
    )
    CACHE_TTL_HOURS: int = Field(
        default=24,
        description="TTL del caché en horas"
    )
    
    # ==================
    # Seguridad
    # ==================
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="Orígenes permitidos para CORS"
    )
    MAX_UPLOAD_TIMEOUT: int = Field(
        default=600,
        description="Timeout para upload en segundos"
    )
    
    # ==================
    # Validadores
    # ==================
    
    @field_validator('UPLOAD_FOLDER', 'CONVERTED_FOLDER', 'LOGS_FOLDER', 'TEMP_FOLDER', mode='before')
    @classmethod
    def create_directories(cls, v):
        """Crear directorios si no existen."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @field_validator('ENV')
    @classmethod
    def validate_env(cls, v):
        """Validar que el entorno sea válido."""
        valid_envs = ['development', 'production', 'testing']
        if v not in valid_envs:
            raise ValueError(f'ENV must be one of {valid_envs}')
        return v
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        """Validar nivel de logging."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of {valid_levels}')
        return v.upper()
    
    @field_validator('MAX_FILE_SIZE')
    @classmethod
    def validate_max_file_size(cls, v):
        """Validar tamaño máximo de archivo."""
        min_size = 1 * 1024 * 1024  # 1MB
        max_size = 10 * 1024 * 1024 * 1024  # 10GB
        if not (min_size <= v <= max_size):
            raise ValueError(f'MAX_FILE_SIZE must be between {min_size} and {max_size} bytes')
        return v
    
    @field_validator('OCR_MAX_PAGES')
    @classmethod
    def validate_ocr_max_pages(cls, v):
        """Validar máximo de páginas OCR."""
        if v <= 0:
            raise ValueError('OCR_MAX_PAGES must be greater than 0')
        if v > 1000:
            raise ValueError('OCR_MAX_PAGES must be less than 1000')
        return v
    
    @field_validator('RATE_LIMIT_REQUESTS', 'RATE_LIMIT_WINDOW')
    @classmethod
    def validate_rate_limit(cls, v):
        """Validar parámetros de rate limiting."""
        if v <= 0:
            raise ValueError('Rate limit values must be greater than 0')
        return v
    
    class Config:
        """Configuración de Pydantic."""
        env_file = ".env"
        case_sensitive = True
        

# Instancia global de configuración
settings = Settings()


# ==================
# Funciones de Ayuda
# ==================

def get_settings() -> Settings:
    """Obtener configuración actual."""
    return settings


def validate_settings() -> bool:
    """
    Validar que la configuración sea correcta.
    
    Returns:
        bool: True si la configuración es válida
        
    Raises:
        InvalidConfigException: Si hay problemas con la configuración
    """
    from .exceptions import InvalidConfigException
    
    try:
        # Validar que los directorios existan
        assert settings.UPLOAD_FOLDER.exists(), "UPLOAD_FOLDER no existe"
        assert settings.CONVERTED_FOLDER.exists(), "CONVERTED_FOLDER no existe"
        assert settings.LOGS_FOLDER.exists(), "LOGS_FOLDER no existe"
        
        # Validar permisos de escritura
        assert os.access(settings.UPLOAD_FOLDER, os.W_OK), "UPLOAD_FOLDER no es escribible"
        assert os.access(settings.CONVERTED_FOLDER, os.W_OK), "CONVERTED_FOLDER no es escribible"
        assert os.access(settings.LOGS_FOLDER, os.W_OK), "LOGS_FOLDER no es escribible"
        
        return True
    except AssertionError as e:
        raise InvalidConfigException(str(e))


# ==================
# Configuraciones por Entorno
# ==================

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
