"""
Tests para validación de archivos (src/validators.py).
"""
import pytest
from unittest.mock import MagicMock, patch
from src.validators import FileValidator
from src.config import Config

class TestFileValidator:

    def test_get_file_category(self):
        """Probar obtención de categoría por MIME type."""
        assert FileValidator.get_file_category('application/pdf') == 'documents'
        assert FileValidator.get_file_category('image/jpeg') == 'images'
        assert FileValidator.get_file_category('audio/mpeg') == 'audio'
        assert FileValidator.get_file_category('video/mp4') == 'video'
        assert FileValidator.get_file_category('application/unknown') is None

    @patch('magic.from_buffer')
    def test_validate_file_valid_pdf(self, mock_magic):
        """Probar validación de un PDF válido."""
        mock_magic.return_value = 'application/pdf'

        file_mock = MagicMock()
        file_mock.filename = 'test.pdf'
        file_mock.read.return_value = b'%PDF-1.4...'
        file_mock.tell.return_value = 1024 # 1KB

        is_valid, error, mime = FileValidator.validate_file(file_mock)

        assert is_valid is True
        assert error is None
        assert mime == 'application/pdf'

    def test_validate_file_no_file(self):
        """Probar validación sin archivo."""
        is_valid, error, mime = FileValidator.validate_file(None)
        assert is_valid is False
        assert error == "No file provided"

    def test_validate_file_empty_filename(self):
        """Probar validación con nombre de archivo vacío."""
        file_mock = MagicMock()
        file_mock.filename = ''

        is_valid, error, mime = FileValidator.validate_file(file_mock)
        assert is_valid is False
        assert error == "No file provided"

    @patch('magic.from_buffer')
    def test_validate_file_invalid_mime(self, mock_magic):
        """Probar archivo con MIME type no permitido."""
        mock_magic.return_value = 'application/x-dosexec'

        file_mock = MagicMock()
        file_mock.filename = 'malware.exe'
        file_mock.read.return_value = b'MZ...'

        is_valid, error, mime = FileValidator.validate_file(file_mock)

        assert is_valid is False
        assert "File type not allowed" in error
        assert mime == 'application/x-dosexec'

    @patch('magic.from_buffer')
    def test_validate_file_too_large(self, mock_magic):
        """Probar archivo que excede el tamaño máximo."""
        mock_magic.return_value = 'application/pdf'

        file_mock = MagicMock()
        file_mock.filename = 'large.pdf'
        file_mock.read.return_value = b'%PDF...'

        # Simular 20MB
        file_mock.tell.return_value = 20 * 1024 * 1024

        # Max size 10MB
        is_valid, error, mime = FileValidator.validate_file(file_mock, max_size_mb=10)

        assert is_valid is False
        assert "File too large" in error
