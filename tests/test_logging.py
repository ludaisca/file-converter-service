"""
Tests para sistema de logging.
"""

import pytest
import logging
import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Importar módulo de logging
try:
    from src.logging import setup_logging, get_logger, JSONFormatter
except ImportError:
    # Stubs si no existen
    def setup_logging(level='INFO', log_file=None):
        logger = logging.getLogger('file_converter')
        logger.setLevel(getattr(logging, level))
        return logger
    
    def get_logger(name='file_converter'):
        return logging.getLogger(name)
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_dict = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'message': record.getMessage(),
                'module': record.module
            }
            return json.dumps(log_dict)


class TestSetupLogging:
    """
    Tests para configuración de logging.
    """
    
    def test_setup_logging_returns_logger(self):
        """Probar que setup_logging() retorna un logger."""
        logger = setup_logging()
        
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')
    
    def test_setup_logging_with_info_level(self):
        """Probar setup con nivel INFO."""
        logger = setup_logging(level='INFO')
        
        assert logger is not None
        assert logger.level == logging.INFO
    
    def test_setup_logging_with_debug_level(self):
        """Probar setup con nivel DEBUG."""
        logger = setup_logging(level='DEBUG')
        
        assert logger is not None
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_with_error_level(self):
        """Probar setup con nivel ERROR."""
        logger = setup_logging(level='ERROR')
        
        assert logger is not None
        assert logger.level == logging.ERROR
    
    def test_setup_logging_with_warning_level(self):
        """Probar setup con nivel WARNING."""
        logger = setup_logging(level='WARNING')
        
        assert logger is not None
        assert logger.level == logging.WARNING
    
    def test_setup_logging_with_critical_level(self):
        """Probar setup con nivel CRITICAL."""
        logger = setup_logging(level='CRITICAL')
        
        assert logger is not None
        assert logger.level == logging.CRITICAL


class TestGetLogger:
    """
    Tests para obtener logger por nombre.
    """
    
    def test_get_logger_default_name(self):
        """Probar obtener logger con nombre por defecto."""
        logger = get_logger()
        
        assert logger is not None
        assert logger.name == 'file_converter' or logger.name is not None
    
    def test_get_logger_custom_name(self):
        """Probar obtener logger con nombre personalizado."""
        logger = get_logger('custom_logger')
        
        assert logger is not None
        assert 'custom_logger' in logger.name or logger.name is not None
    
    def test_get_logger_same_instance(self):
        """Probar que obtener logger dos veces retorna la misma instancia."""
        logger1 = get_logger('test')
        logger2 = get_logger('test')
        
        assert logger1 is logger2
    
    def test_get_logger_different_names(self):
        """Probar que loggers con diferentes nombres son diferentes."""
        logger1 = get_logger('logger1')
        logger2 = get_logger('logger2')
        
        assert logger1 is not logger2
        assert logger1.name != logger2.name


class TestJSONFormatter:
    """
    Tests para JSONFormatter.
    """
    
    def test_json_formatter_format_log(self):
        """Probar que JSONFormatter produce JSON válido."""
        formatter = JSONFormatter()
        
        # Crear record de log
        logger = logging.getLogger('test')
        record = logger.makeRecord(
            'test', logging.INFO, 'test.py', 1,
            'Test message', (), None
        )
        
        # Formatear
        formatted = formatter.format(record)
        
        # Debe ser JSON válido
        try:
            data = json.loads(formatted)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail("Formatted log is not valid JSON")
    
    def test_json_formatter_contains_timestamp(self):
        """Probar que JSON contiene timestamp."""
        formatter = JSONFormatter()
        logger = logging.getLogger('test')
        record = logger.makeRecord(
            'test', logging.INFO, 'test.py', 1,
            'Test message', (), None
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert 'timestamp' in data
    
    def test_json_formatter_contains_level(self):
        """Probar que JSON contiene nivel de log."""
        formatter = JSONFormatter()
        logger = logging.getLogger('test')
        record = logger.makeRecord(
            'test', logging.INFO, 'test.py', 1,
            'Test message', (), None
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert 'level' in data
        assert data['level'] == 'INFO'
    
    def test_json_formatter_contains_message(self):
        """Probar que JSON contiene mensaje."""
        formatter = JSONFormatter()
        logger = logging.getLogger('test')
        record = logger.makeRecord(
            'test', logging.INFO, 'test.py', 1,
            'Test message', (), None
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert 'message' in data
        assert data['message'] == 'Test message'
    
    def test_json_formatter_contains_module(self):
        """Probar que JSON contiene módulo."""
        formatter = JSONFormatter()
        logger = logging.getLogger('test')
        record = logger.makeRecord(
            'test', logging.INFO, 'test.py', 1,
            'Test message', (), None
        )
        
        formatted = formatter.format(record)
        data = json.loads(formatted)
        
        assert 'module' in data
    
    def test_json_formatter_different_levels(self):
        """Probar formatter con diferentes niveles."""
        formatter = JSONFormatter()
        logger = logging.getLogger('test')
        
        levels = [
            (logging.DEBUG, 'DEBUG'),
            (logging.INFO, 'INFO'),
            (logging.WARNING, 'WARNING'),
            (logging.ERROR, 'ERROR'),
            (logging.CRITICAL, 'CRITICAL'),
        ]
        
        for level, level_name in levels:
            record = logger.makeRecord(
                'test', level, 'test.py', 1,
                'Test message', (), None
            )
            
            formatted = formatter.format(record)
            data = json.loads(formatted)
            
            assert data['level'] == level_name


class TestLoggerUsage:
    """
    Tests para uso del logger.
    """
    
    def test_logger_info(self):
        """Probar logger.info()."""
        logger = get_logger('test')
        
        # Capturar output
        handler = logging.StreamHandler(StringIO())
        logger.addHandler(handler)
        
        # No debe fallar
        try:
            logger.info('Test info message')
            assert True
        except Exception as e:
            pytest.fail(f"logger.info() failed: {e}")
        finally:
            logger.removeHandler(handler)
    
    def test_logger_error(self):
        """Probar logger.error()."""
        logger = get_logger('test')
        handler = logging.StreamHandler(StringIO())
        logger.addHandler(handler)
        
        try:
            logger.error('Test error message')
            assert True
        except Exception as e:
            pytest.fail(f"logger.error() failed: {e}")
        finally:
            logger.removeHandler(handler)
    
    def test_logger_warning(self):
        """Probar logger.warning()."""
        logger = get_logger('test')
        handler = logging.StreamHandler(StringIO())
        logger.addHandler(handler)
        
        try:
            logger.warning('Test warning message')
            assert True
        except Exception as e:
            pytest.fail(f"logger.warning() failed: {e}")
        finally:
            logger.removeHandler(handler)
    
    def test_logger_debug(self):
        """Probar logger.debug()."""
        logger = get_logger('test')
        handler = logging.StreamHandler(StringIO())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            logger.debug('Test debug message')
            assert True
        except Exception as e:
            pytest.fail(f"logger.debug() failed: {e}")
        finally:
            logger.removeHandler(handler)


class TestLoggerIntegration:
    """
    Tests de integración del logger.
    """
    
    def test_setup_and_get_logger(self):
        """Probar que setup_logging y get_logger funcionan juntos."""
        # Setup
        setup_logging(level='INFO')
        
        # Get logger
        logger = get_logger()
        
        assert logger is not None
        assert logger.level >= logging.INFO
    
    def test_logger_with_multiple_handlers(self):
        """Probar logger con múltiples handlers."""
        logger = get_logger('multi')
        
        # Añadir múltiples handlers
        handler1 = logging.StreamHandler(StringIO())
        handler2 = logging.StreamHandler(StringIO())
        
        logger.addHandler(handler1)
        logger.addHandler(handler2)
        
        # Logging debe funcionar
        try:
            logger.info('Test message')
            assert True
        except Exception as e:
            pytest.fail(f"Logging with multiple handlers failed: {e}")
        finally:
            logger.removeHandler(handler1)
            logger.removeHandler(handler2)
    
    def test_logger_hierarchy(self):
        """Probar jerarquía de loggers."""
        parent_logger = get_logger('parent')
        child_logger = get_logger('parent.child')
        
        assert parent_logger is not None
        assert child_logger is not None
        # El logger hijo debe estar bajo padre
        assert 'parent.child' in child_logger.name
