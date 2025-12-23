"""
Sistema de excepciones personalizado para File Converter Service.
Define excepciones específicas y estructuradas para mejor manejo de errores.
"""

from typing import Optional
from datetime import datetime


class FileConverterException(Exception):
    """
    Clase base para todas las excepciones del servicio.
    
    Atributos:
        message: Descripción del error
        error_code: Código único del error
        status_code: Código HTTP asociado
        details: Información adicional del error
    """
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convertir excepción a diccionario para respuesta JSON."""
        return {
            'success': False,
            'error': self.message,
            'error_code': self.error_code,
            'timestamp': self.timestamp,
            'details': self.details if self.details else None
        }


class InvalidFileException(FileConverterException):
    """Se lanza cuando el archivo es inválido."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code='INVALID_FILE',
            status_code=400,
            details=details
        )


class UnsupportedFormatException(FileConverterException):
    """Se lanza cuando el formato no está soportado."""
    
    def __init__(self, format_name: str, supported_formats: list = None):
        message = f"Unsupported format: {format_name}"
        details = {
            'provided_format': format_name,
            'supported_formats': supported_formats
        } if supported_formats else {}
        
        super().__init__(
            message=message,
            error_code='UNSUPPORTED_FORMAT',
            status_code=400,
            details=details
        )


class ConversionFailedException(FileConverterException):
    """Se lanza cuando la conversión falla."""
    
    def __init__(
        self,
        message: str,
        source_format: str = None,
        target_format: str = None
    ):
        details = {}
        if source_format:
            details['source_format'] = source_format
        if target_format:
            details['target_format'] = target_format
        
        super().__init__(
            message=message,
            error_code='CONVERSION_FAILED',
            status_code=500,
            details=details
        )


class FileTooLargeException(FileConverterException):
    """Se lanza cuando el archivo excede el tamaño máximo."""
    
    def __init__(self, file_size_mb: float, max_size_mb: float):
        message = f"File too large: {file_size_mb:.2f}MB (maximum: {max_size_mb:.2f}MB)"
        
        super().__init__(
            message=message,
            error_code='FILE_TOO_LARGE',
            status_code=413,
            details={
                'file_size_mb': file_size_mb,
                'max_size_mb': max_size_mb
            }
        )


class FileNotFoundException(FileConverterException):
    """Se lanza cuando el archivo no existe."""
    
    def __init__(self, filename: str):
        message = f"File not found: {filename}"
        
        super().__init__(
            message=message,
            error_code='FILE_NOT_FOUND',
            status_code=404,
            details={'filename': filename}
        )


class OCRDisabledException(FileConverterException):
    """Se lanza cuando OCR está deshabilitado."""
    
    def __init__(self):
        super().__init__(
            message='OCR functionality is disabled',
            error_code='OCR_DISABLED',
            status_code=503
        )


class OCRProcessingException(FileConverterException):
    """Se lanza cuando OCR falla."""
    
    def __init__(self, message: str, language: str = None):
        details = {}
        if language:
            details['language'] = language
        
        super().__init__(
            message=message,
            error_code='OCR_PROCESSING_ERROR',
            status_code=500,
            details=details
        )


class InvalidConfigException(FileConverterException):
    """Se lanza cuando hay problemas con la configuración."""
    
    def __init__(self, message: str, config_key: str = None):
        details = {}
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(
            message=message,
            error_code='INVALID_CONFIG',
            status_code=500,
            details=details
        )


class RateLimitExceededException(FileConverterException):
    """Se lanza cuando se excede el límite de rate limiting."""
    
    def __init__(self, retry_after: int = None):
        message = 'Rate limit exceeded. Please try again later.'
        details = {}
        if retry_after:
            details['retry_after_seconds'] = retry_after
        
        super().__init__(
            message=message,
            error_code='RATE_LIMIT_EXCEEDED',
            status_code=429,
            details=details
        )


class URLDownloadException(FileConverterException):
    """Se lanza cuando falla la descarga desde URL."""
    
    def __init__(self, url: str, reason: str):
        message = f"Failed to download file from URL: {reason}"
        
        super().__init__(
            message=message,
            error_code='URL_DOWNLOAD_FAILED',
            status_code=400,
            details={'url': url, 'reason': reason}
        )

class SecurityException(FileConverterException):
    """Se lanza cuando el archivo no pasa validaciones de seguridad (ej. virus)."""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            error_code='SECURITY_VIOLATION',
            status_code=403,
            details=details
        )
