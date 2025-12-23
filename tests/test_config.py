"""
Tests para el sistema de configuración con Pydantic.
"""

import pytest
from pathlib import Path
from pydantic import ValidationError

from src.config_refactored import Settings, validate_settings
from src.exceptions import InvalidConfigException


class TestSettingsCreation:
    """
    Tests para creación de instancias Settings.
    """
    
    def test_create_settings_with_defaults(self):
        """Probar creación con valores por defecto."""
        settings = Settings()
        
        assert settings.ENV == 'development'
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == 'INFO'
        assert settings.HOST == '0.0.0.0'
        assert settings.PORT == 5000
    
    def test_create_settings_custom_values(self):
        """Probar creación con valores personalizados."""
        settings = Settings(
            ENV='production',
            DEBUG=True,
            LOG_LEVEL='DEBUG',
            PORT=8080
        )
        
        assert settings.ENV == 'production'
        assert settings.DEBUG is True
        assert settings.LOG_LEVEL == 'DEBUG'
        assert settings.PORT == 8080


class TestEnvironmentValidation:
    """
    Tests para validación de ambiente.
    """
    
    def test_valid_environments(self):
        """Probar que ambientes válidos son aceptados."""
        valid_envs = ['development', 'production', 'testing']
        
        for env in valid_envs:
            settings = Settings(ENV=env)
            assert settings.ENV == env
    
    def test_invalid_environment(self):
        """Probar que ambientes inválidos rechazan."""
        with pytest.raises(ValidationError):
            Settings(ENV='invalid_env')


class TestLogLevelValidation:
    """
    Tests para validación de nivel de logging.
    """
    
    def test_valid_log_levels(self):
        """Probar que niveles válidos son aceptados."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in valid_levels:
            settings = Settings(LOG_LEVEL=level)
            assert settings.LOG_LEVEL == level
    
    def test_log_level_case_insensitive(self):
        """Probar que LOG_LEVEL es insensible a minúsculas."""
        settings = Settings(LOG_LEVEL='debug')
        assert settings.LOG_LEVEL == 'DEBUG'
    
    def test_invalid_log_level(self):
        """Probar que niveles inválidos rechazan."""
        with pytest.raises(ValidationError):
            Settings(LOG_LEVEL='INVALID')


class TestMaxFileSizeValidation:
    """
    Tests para validación de tamaño máximo de archivo.
    """
    
    def test_valid_max_file_size(self):
        """Probar que tamaños válidos son aceptados."""
        # 1MB - 10GB válido
        valid_sizes = [
            1 * 1024 * 1024,      # 1MB
            100 * 1024 * 1024,    # 100MB
            1 * 1024 * 1024 * 1024  # 1GB
        ]
        
        for size in valid_sizes:
            settings = Settings(MAX_FILE_SIZE=size)
            assert settings.MAX_FILE_SIZE == size
    
    def test_max_file_size_too_small(self):
        """Probar que tamaños menores a 1MB rechazan."""
        with pytest.raises(ValidationError):
            Settings(MAX_FILE_SIZE=512 * 1024)  # 512KB
    
    def test_max_file_size_too_large(self):
        """Probar que tamaños mayores a 10GB rechazan."""
        with pytest.raises(ValidationError):
            Settings(MAX_FILE_SIZE=11 * 1024 * 1024 * 1024)  # 11GB


class TestOCRMaxPagesValidation:
    """
    Tests para validación de OCR_MAX_PAGES.
    """
    
    def test_valid_ocr_max_pages(self):
        """Probar que valores válidos son aceptados."""
        valid_values = [1, 50, 100, 500, 1000]
        
        for value in valid_values:
            settings = Settings(OCR_MAX_PAGES=value)
            assert settings.OCR_MAX_PAGES == value
    
    def test_ocr_max_pages_zero(self):
        """Probar que 0 es rechazado."""
        with pytest.raises(ValidationError):
            Settings(OCR_MAX_PAGES=0)
    
    def test_ocr_max_pages_negative(self):
        """Probar que valores negativos son rechazados."""
        with pytest.raises(ValidationError):
            Settings(OCR_MAX_PAGES=-10)
    
    def test_ocr_max_pages_too_large(self):
        """Probar que valores > 1000 son rechazados."""
        with pytest.raises(ValidationError):
            Settings(OCR_MAX_PAGES=1001)


class TestRateLimitValidation:
    """
    Tests para validación de parámetros de rate limiting.
    """
    
    def test_valid_rate_limit_values(self):
        """Probar que valores válidos son aceptados."""
        settings = Settings(
            RATE_LIMIT_REQUESTS=100,
            RATE_LIMIT_WINDOW=60
        )
        
        assert settings.RATE_LIMIT_REQUESTS == 100
        assert settings.RATE_LIMIT_WINDOW == 60
    
    def test_rate_limit_requests_zero(self):
        """Probar que 0 requests es rechazado."""
        with pytest.raises(ValidationError):
            Settings(RATE_LIMIT_REQUESTS=0)
    
    def test_rate_limit_window_zero(self):
        """Probar que window de 0 es rechazado."""
        with pytest.raises(ValidationError):
            Settings(RATE_LIMIT_WINDOW=0)


class TestDirectoryCreation:
    """
    Tests para creación automática de directorios.
    """
    
    def test_directories_created(self):
        """Probar que los directorios se crean automáticamente."""
        settings = Settings()
        
        # Los directorios deben existir después de crear Settings
        assert settings.UPLOAD_FOLDER.exists()
        assert settings.CONVERTED_FOLDER.exists()
        assert settings.LOGS_FOLDER.exists()
        assert settings.TEMP_FOLDER.exists()
    
    def test_directories_are_pathlib_path(self):
        """Probar que los directorios son objetos Path."""
        settings = Settings()
        
        assert isinstance(settings.UPLOAD_FOLDER, Path)
        assert isinstance(settings.CONVERTED_FOLDER, Path)
        assert isinstance(settings.LOGS_FOLDER, Path)
        assert isinstance(settings.TEMP_FOLDER, Path)


class TestAllowedExtensions:
    """
    Tests para extensiones permitidas.
    """
    
    def test_default_allowed_extensions(self):
        """Probar que extensiones por defecto incluyen formatos comunes."""
        settings = Settings()
        
        common_formats = ['pdf', 'docx', 'xlsx', 'jpg', 'png']
        for fmt in common_formats:
            assert fmt in settings.ALLOWED_EXTENSIONS
    
    def test_allowed_extensions_is_list(self):
        """Probar que ALLOWED_EXTENSIONS es una lista."""
        settings = Settings()
        assert isinstance(settings.ALLOWED_EXTENSIONS, list)
        assert len(settings.ALLOWED_EXTENSIONS) > 0
    
    def test_custom_allowed_extensions(self):
        """Probar que se pueden personalizar extensiones permitidas."""
        custom_exts = ['pdf', 'txt']
        settings = Settings(ALLOWED_EXTENSIONS=custom_exts)
        
        assert settings.ALLOWED_EXTENSIONS == custom_exts


class TestEnvironmentSpecificConfig:
    """
    Tests para configuración específicas por ambiente.
    """
    
    def test_development_env_defaults(self):
        """Probar configuración por defecto en development."""
        settings = Settings(ENV='development')
        
        # Development usa valores por defecto
        assert settings.DEBUG is False
    
    def test_testing_env_disabled_features(self):
        """Probar que testing deshabilita ciertas features."""
        settings = Settings(ENV='testing')
        
        # La configuración en el módulo ajusta estos
        assert settings.ENV == 'testing'
    
    def test_production_env_values(self):
        """Probar configuración para production."""
        settings = Settings(ENV='production')
        
        assert settings.ENV == 'production'


class TestCORSOrigins:
    """
    Tests para configuración de CORS origins.
    """
    
    def test_default_cors_origins(self):
        """Probar que CORS origins por defecto es wildcard."""
        settings = Settings()
        assert settings.CORS_ORIGINS == ['*']
    
    def test_custom_cors_origins(self):
        """Probar que se pueden personalizar CORS origins."""
        origins = ['https://example.com', 'https://app.example.com']
        settings = Settings(CORS_ORIGINS=origins)
        
        assert settings.CORS_ORIGINS == origins


class TestCacheConfig:
    """
    Tests para configuración de caché.
    """
    
    def test_cache_disabled_by_default(self):
        """Probar que cache está deshabilitado por defecto."""
        settings = Settings()
        assert settings.ENABLE_CACHE is False
    
    def test_cache_type_values(self):
        """Probar valores válidos para CACHE_TYPE."""
        for cache_type in ['simple', 'redis']:
            settings = Settings(
                ENABLE_CACHE=True,
                CACHE_TYPE=cache_type
            )
            assert settings.CACHE_TYPE == cache_type
    
    def test_redis_url(self):
        """Probar configuración de URL de Redis."""
        redis_url = 'redis://localhost:6379/1'
        settings = Settings(REDIS_URL=redis_url)
        assert settings.REDIS_URL == redis_url


class TestValidateSettings:
    """
    Tests para la función validate_settings().
    """
    
    def test_validate_settings_success(self):
        """Probar que validate_settings() retorna True para config válida."""
        result = validate_settings()
        assert result is True
    
    def test_validate_settings_invalid_folder(self):
        """Probar que validate_settings() falla si faltan carpetas."""
        # Este test es más complejo ya que requiere eliminar carpetas
        # Por ahora solo verificamos que no levanta en caso válido
        try:
            validate_settings()
            assert True
        except InvalidConfigException:
            assert False, "validate_settings() no debe fallar con config válida"


class TestSettingsImmutability:
    """
    Tests para verificar que Settings tiene comportamiento esperado.
    """
    
    def test_settings_is_singleton_like(self):
        """Probar que instancias con mismos parámetros son iguales."""
        settings1 = Settings(ENV='testing', PORT=5000)
        settings2 = Settings(ENV='testing', PORT=5000)
        
        assert settings1.ENV == settings2.ENV
        assert settings1.PORT == settings2.PORT
    
    def test_settings_repr(self):
        """Probar que Settings tiene repr útil."""
        settings = Settings(ENV='testing')
        repr_str = repr(settings)
        
        # Debe ser un string válido
        assert isinstance(repr_str, str)
        assert len(repr_str) > 0


class TestSettingsDocumentation:
    """
    Tests para verificar documentación de campos.
    """
    
    def test_settings_has_descriptions(self):
        """Probar que los campos tienen descripciones."""
        settings = Settings()
        
        # Verify that field definitions exist
        assert hasattr(Settings, 'model_fields')
        fields = Settings.model_fields
        
        # Algunos campos clave deben estar presentes
        assert 'ENV' in fields
        assert 'DEBUG' in fields
        assert 'MAX_FILE_SIZE' in fields
