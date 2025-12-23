"""
Configuración de logging estructurado para la aplicación.
"""

import logging
from pathlib import Path
from datetime import datetime
import json

from src.config_refactored import settings


class JSONFormatter(logging.Formatter):
    """
    Formateador que produce logs en formato JSON.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatear registro como JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Agregar excepción si existe
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Agregar atributos personalizados
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> logging.Logger:
    """
    Configurar logging de la aplicación.
    
    Returns:
        logging.Logger: Logger configurado
    """
    
    # Crear logger base
    logger = logging.getLogger('file-converter')
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (solo si se especifica log folder)
    if settings.LOGS_FOLDER:
        log_file = settings.LOGS_FOLDER / f"file-converter-{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Siempre DEBUG en archivo
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Instancia global de logger
logger = setup_logging()


def get_logger(name: str) -> logging.Logger:
    """
    Obtener logger con nombre específico.
    
    Args:
        name: Nombre del logger
    
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(f"file-converter.{name}")
