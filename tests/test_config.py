"""
Tests para configuración y validación.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Importar configuración a testear
from src.config import Settings, validate_settings, get_settings


class TestSettings:
    """
    Tests para clase Settings (Pydantic).
    """
    
    def test_default_values(self):
        """Probar valores por defecto."""
        settings = Settings()
        
        assert settings.DEBUG is False
        assert settings.ENV == 'development'
        assert settings.LOG_LEVEL == 'INFO'
        assert settings.PORT == 5000
        assert settings.WORKERS == 4
        assert settings.ENABLE_OCR is True
        
    def test_env_validation(self):
        """Probar validación de entorno."""
        # Valor válido
        settings = Settings(ENV='production')
        assert settings.ENV == 'production'
        
        # Valor inválido
        with pytest.raises(ValueError):
            Settings(ENV='invalid')

    def test_log_level_validation(self):
        """Probar validación de nivel de log."""
        # Valor válido
        settings = Settings(LOG_LEVEL='DEBUG')
        assert settings.LOG_LEVEL == 'DEBUG'
        
        # Case insensitive
        settings = Settings(LOG_LEVEL='debug')
        assert settings.LOG_LEVEL == 'DEBUG'

        # Valor inválido
        with pytest.raises(ValueError):
            Settings(LOG_LEVEL='INVALID')

    def test_file_size_validation(self):
        """Probar validación de tamaño de archivo."""
        # Valor válido (10MB)
        settings = Settings(MAX_FILE_SIZE=10 * 1024 * 1024)
        assert settings.MAX_FILE_SIZE == 10 * 1024 * 1024
        
        # Muy pequeño (<1MB)
        with pytest.raises(ValueError):
            Settings(MAX_FILE_SIZE=1024)

        # Muy grande (>10GB)
        with pytest.raises(ValueError):
            Settings(MAX_FILE_SIZE=11 * 1024 * 1024 * 1024)

    def test_ocr_pages_validation(self):
        """Probar validación de páginas OCR."""
        # Valor válido
        settings = Settings(OCR_MAX_PAGES=10)
        assert settings.OCR_MAX_PAGES == 10
        
        # Cero o negativo
        with pytest.raises(ValueError):
            Settings(OCR_MAX_PAGES=0)

        # Excesivo
        with pytest.raises(ValueError):
            Settings(OCR_MAX_PAGES=2000)

    def test_rate_limit_validation(self):
        """Probar validación de rate limit."""
        # Valor válido
        settings = Settings(RATE_LIMIT_REQUESTS=50)
        assert settings.RATE_LIMIT_REQUESTS == 50
        
        # Cero o negativo
        with pytest.raises(ValueError):
            Settings(RATE_LIMIT_REQUESTS=0)

    def test_directory_creation(self, tmp_path):
        """Probar creación automática de directorios."""
        upload_dir = tmp_path / "uploads"
        
        # Al instanciar settings, debe crear directorios
        # Nota: Esto depende de que el validador se ejecute.
        # En Pydantic v2 los validadores 'before' se ejecutan antes de asignar.
        
        settings = Settings(UPLOAD_FOLDER=upload_dir)
        
        assert upload_dir.exists()
        assert upload_dir.is_dir()


class TestValidateSettings:
    """
    Tests para función validate_settings().
    """
    
    @patch('src.config.settings')
    def test_valid_settings(self, mock_settings):
        """Probar configuración válida."""
        # Mock settings
        mock_settings.UPLOAD_FOLDER = MagicMock()
        mock_settings.UPLOAD_FOLDER.exists.return_value = True
        mock_settings.CONVERTED_FOLDER = MagicMock()
        mock_settings.CONVERTED_FOLDER.exists.return_value = True
        mock_settings.LOGS_FOLDER = MagicMock()
        mock_settings.LOGS_FOLDER.exists.return_value = True
        
        # Mock os.access
        with patch('os.access', return_value=True):
            result = validate_settings()
            assert result is True

    @patch('src.config.settings')
    def test_missing_directory(self, mock_settings):
        """Probar directorio faltante."""
        mock_settings.UPLOAD_FOLDER = MagicMock()
        mock_settings.UPLOAD_FOLDER.exists.return_value = False
        
        from src.exceptions import InvalidConfigException
        
        with pytest.raises(InvalidConfigException):
            validate_settings()

    @patch('src.config.settings')
    def test_no_write_permission(self, mock_settings):
        """Probar falta de permisos de escritura."""
        mock_settings.UPLOAD_FOLDER = MagicMock()
        mock_settings.UPLOAD_FOLDER.exists.return_value = True
        # ... configurar otros directorios ...
        mock_settings.CONVERTED_FOLDER.exists.return_value = True
        mock_settings.LOGS_FOLDER.exists.return_value = True
        
        # Mock os.access returning False
        with patch('os.access', return_value=False):
            from src.exceptions import InvalidConfigException

            with pytest.raises(InvalidConfigException):
                validate_settings()


class TestGetSettings:
    """
    Tests para get_settings().
    """
    
    def test_returns_settings_instance(self):
        """Probar que retorna instancia de Settings."""
        settings = get_settings()
        assert isinstance(settings, Settings)
        
    def test_singleton_behavior(self):
        """Probar que retorna la misma instancia (singleton implícito)."""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2
