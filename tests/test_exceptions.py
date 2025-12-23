"""
Tests para el sistema de excepciones personalizado.
"""

import pytest
from datetime import datetime

from src.exceptions import (
    FileConverterException,
    InvalidFileException,
    UnsupportedFormatException,
    ConversionFailedException,
    FileTooLargeException,
    FileNotFoundException,
    OCRDisabledException,
    OCRProcessingException,
    InvalidConfigException,
    RateLimitExceededException,
    URLDownloadException
)


class TestFileConverterException:
    """
    Tests para la clase base FileConverterException.
    """
    
    def test_create_base_exception(self):
        """Probar creación de excepción base."""
        exc = FileConverterException(
            message='Test error',
            error_code='TEST_ERROR',
            status_code=500
        )
        
        assert exc.message == 'Test error'
        assert exc.error_code == 'TEST_ERROR'
        assert exc.status_code == 500
        assert exc.timestamp is not None
    
    def test_exception_to_dict(self):
        """Probar conversión a diccionario JSON."""
        exc = FileConverterException(
            message='Test error',
            error_code='TEST_ERROR',
            status_code=500
        )
        
        result = exc.to_dict()
        
        assert result['success'] is False
        assert result['error'] == 'Test error'
        assert result['error_code'] == 'TEST_ERROR'
        assert 'timestamp' in result
        assert result['details'] is None
    
    def test_exception_with_details(self):
        """Probar excepción con detalles adicionales."""
        details = {'key': 'value', 'nested': {'data': 'here'}}
        exc = FileConverterException(
            message='Test error',
            error_code='TEST_ERROR',
            status_code=500,
            details=details
        )
        
        result = exc.to_dict()
        
        assert result['details'] == details
    
    def test_exception_timestamp_format(self):
        """Probar que timestamp está en formato ISO 8601."""
        exc = FileConverterException(
            message='Test',
            error_code='TEST',
            status_code=500
        )
        
        # Intentar parsear como ISO 8601
        try:
            datetime.fromisoformat(exc.timestamp)
            assert True
        except ValueError:
            assert False, "Timestamp no está en formato ISO 8601"


class TestInvalidFileException:
    """
    Tests para InvalidFileException.
    """
    
    def test_create_invalid_file_exception(self):
        """Probar creación de excepción de archivo inválido."""
        exc = InvalidFileException('Invalid file format')
        
        assert exc.error_code == 'INVALID_FILE'
        assert exc.status_code == 400
        assert exc.message == 'Invalid file format'
    
    def test_invalid_file_with_details(self):
        """Probar excepción con detalles."""
        exc = InvalidFileException(
            'Invalid file',
            details={'filename': 'test.xyz'}
        )
        
        result = exc.to_dict()
        
        assert result['details']['filename'] == 'test.xyz'


class TestUnsupportedFormatException:
    """
    Tests para UnsupportedFormatException.
    """
    
    def test_create_unsupported_format(self):
        """Probar creación de excepción de formato no soportado."""
        exc = UnsupportedFormatException('xyz')
        
        assert exc.error_code == 'UNSUPPORTED_FORMAT'
        assert exc.status_code == 400
        assert 'xyz' in exc.message
    
    def test_unsupported_format_with_supported_list(self):
        """Probar que incluye lista de formatos soportados."""
        supported = ['pdf', 'docx', 'xlsx']
        exc = UnsupportedFormatException('xyz', supported_formats=supported)
        
        result = exc.to_dict()
        
        assert result['details']['provided_format'] == 'xyz'
        assert result['details']['supported_formats'] == supported


class TestFileTooLargeException:
    """
    Tests para FileTooLargeException.
    """
    
    def test_create_file_too_large(self):
        """Probar creación de excepción de archivo muy grande."""
        exc = FileTooLargeException(600.5, 500.0)
        
        assert exc.error_code == 'FILE_TOO_LARGE'
        assert exc.status_code == 413
        assert '600.50MB' in exc.message
        assert '500.00MB' in exc.message
    
    def test_file_too_large_details(self):
        """Probar detalles de excepción."""
        exc = FileTooLargeException(600.5, 500.0)
        result = exc.to_dict()
        
        assert result['details']['file_size_mb'] == 600.5
        assert result['details']['max_size_mb'] == 500.0


class TestFileNotFoundException:
    """
    Tests para FileNotFoundException.
    """
    
    def test_create_file_not_found(self):
        """Probar creación de excepción de archivo no encontrado."""
        exc = FileNotFoundException('missing.pdf')
        
        assert exc.error_code == 'FILE_NOT_FOUND'
        assert exc.status_code == 404
        assert 'missing.pdf' in exc.message
    
    def test_file_not_found_details(self):
        """Probar detalles de archivo."""
        exc = FileNotFoundException('missing.pdf')
        result = exc.to_dict()
        
        assert result['details']['filename'] == 'missing.pdf'


class TestConversionFailedException:
    """
    Tests para ConversionFailedException.
    """
    
    def test_create_conversion_failed(self):
        """Probar creación de excepción de conversión fallida."""
        exc = ConversionFailedException('Unknown error')
        
        assert exc.error_code == 'CONVERSION_FAILED'
        assert exc.status_code == 500
    
    def test_conversion_failed_with_formats(self):
        """Probar con formatos de origen y destino."""
        exc = ConversionFailedException(
            'Error',
            source_format='.pdf',
            target_format='.docx'
        )
        
        result = exc.to_dict()
        
        assert result['details']['source_format'] == '.pdf'
        assert result['details']['target_format'] == '.docx'


class TestOCRExceptions:
    """
    Tests para excepciones relacionadas con OCR.
    """
    
    def test_ocr_disabled(self):
        """Probar excepción cuando OCR está deshabilitado."""
        exc = OCRDisabledException()
        
        assert exc.error_code == 'OCR_DISABLED'
        assert exc.status_code == 503
    
    def test_ocr_processing_error(self):
        """Probar excepción de error en OCR."""
        exc = OCRProcessingException('Failed to extract text', language='spa')
        
        assert exc.error_code == 'OCR_PROCESSING_ERROR'
        assert exc.status_code == 500
        
        result = exc.to_dict()
        assert result['details']['language'] == 'spa'


class TestRateLimitException:
    """
    Tests para RateLimitExceededException.
    """
    
    def test_rate_limit_exceeded(self):
        """Probar excepción de rate limit."""
        exc = RateLimitExceededException(retry_after=60)
        
        assert exc.error_code == 'RATE_LIMIT_EXCEEDED'
        assert exc.status_code == 429
        
        result = exc.to_dict()
        assert result['details']['retry_after_seconds'] == 60


class TestURLDownloadException:
    """
    Tests para URLDownloadException.
    """
    
    def test_url_download_failed(self):
        """Probar excepción de descarga desde URL."""
        exc = URLDownloadException(
            'https://example.com/file.pdf',
            'Connection timeout'
        )
        
        assert exc.error_code == 'URL_DOWNLOAD_FAILED'
        assert exc.status_code == 400
        
        result = exc.to_dict()
        assert result['details']['url'] == 'https://example.com/file.pdf'
        assert result['details']['reason'] == 'Connection timeout'


class TestInvalidConfigException:
    """
    Tests para InvalidConfigException.
    """
    
    def test_invalid_config(self):
        """Probar excepción de configuración inválida."""
        exc = InvalidConfigException(
            'Invalid setting value',
            config_key='MAX_FILE_SIZE'
        )
        
        assert exc.error_code == 'INVALID_CONFIG'
        assert exc.status_code == 500
        
        result = exc.to_dict()
        assert result['details']['config_key'] == 'MAX_FILE_SIZE'


class TestExceptionInheritance:
    """
    Tests para verificar herencia de excepciones.
    """
    
    def test_all_exceptions_inherit_from_base(self):
        """Verificar que todas las excepciones heredan de FileConverterException."""
        exceptions = [
            InvalidFileException('test'),
            UnsupportedFormatException('test'),
            ConversionFailedException('test'),
            FileTooLargeException(100, 50),
            FileNotFoundException('test'),
            OCRDisabledException(),
            OCRProcessingException('test'),
            InvalidConfigException('test'),
            RateLimitExceededException(),
            URLDownloadException('url', 'reason')
        ]
        
        for exc in exceptions:
            assert isinstance(exc, FileConverterException)
            assert hasattr(exc, 'to_dict')
            assert hasattr(exc, 'error_code')
            assert hasattr(exc, 'status_code')


class TestExceptionJSON:
    """
    Tests para verificar que todas las excepciones retornan JSON válido.
    """
    
    def test_all_exceptions_to_dict_structure(self):
        """Verificar que to_dict() tiene estructura requerida."""
        exceptions = [
            InvalidFileException('test'),
            UnsupportedFormatException('test'),
            FileTooLargeException(100, 50),
            FileNotFoundException('test'),
        ]
        
        for exc in exceptions:
            result = exc.to_dict()
            
            # Campos obligatorios
            assert 'success' in result
            assert result['success'] is False
            assert 'error' in result
            assert 'error_code' in result
            assert 'timestamp' in result
            assert 'details' in result
