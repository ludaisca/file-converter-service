"""
Configuración de Rate Limiting
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import Config
import os


def get_rate_limit_key():
    """
    Obtiene la clave para rate limiting.
    Prioriza API key si existe, sino usa IP.
    """
    from flask import request
    
    # Si hay API key en el header, usar esa
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"api_key:{api_key}"
    
    # Si no, usar IP
    return f"ip:{get_remote_address()}"


# Configuración de rate limits desde variables de entorno
RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')

# Limites por defecto
DEFAULT_LIMITS = [
    "200 per day",
    "50 per hour"
]

CONVERT_LIMIT = os.getenv('CONVERT_RATELIMIT', '10 per minute')
HEALTH_LIMIT = os.getenv('HEALTH_RATELIMIT', '30 per minute')


def init_limiter(app):
    """
    Inicializa el rate limiter con la aplicación Flask
    
    Args:
        app: Instancia de Flask
        
    Returns:
        Limiter: Instancia configurada de Flask-Limiter
    """
    limiter = Limiter(
        app=app,
        key_func=get_rate_limit_key,
        default_limits=DEFAULT_LIMITS,
        storage_uri=RATELIMIT_STORAGE_URL,
        storage_options={},
        # Headers para informar al cliente
        headers_enabled=True,
        # Strategy: fixed-window, moving-window, fixed-window-elastic-expiry
        strategy='fixed-window',
        # Mensaje de error personalizado
        default_limits_exempt_when=lambda: False
    )
    
    # Handler para errores de rate limit
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {
            'error': 'Rate limit exceeded',
            'message': str(e.description),
            'retry_after': e.description
        }, 429
    
    return limiter
