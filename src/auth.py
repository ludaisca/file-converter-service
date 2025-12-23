"""
Sistema de autenticación con API Keys
"""
import os
import secrets
from functools import wraps
from flask import request, jsonify


class APIKeyAuth:
    """
    Gestor de autenticación con API Keys
    """
    
    def __init__(self):
        """
        Inicializa el sistema de autenticación.
        Las API keys se cargan desde variables de entorno.
        """
        # API keys válidas (formato: API_KEY_1, API_KEY_2, etc.)
        self.valid_keys = set()
        
        # Cargar API keys desde env vars
        self._load_api_keys_from_env()
        
        # Flag para habilitar/deshabilitar autenticación
        self.enabled = os.getenv('ENABLE_API_AUTH', 'False').lower() == 'true'
        
    def _load_api_keys_from_env(self):
        """
        Carga API keys desde variables de entorno.
        Busca variables con patrón API_KEY_X
        """
        # Buscar todas las variables API_KEY_*
        for key, value in os.environ.items():
            if key.startswith('API_KEY_') and value:
                self.valid_keys.add(value.strip())
        
        # Si no hay keys configuradas, generar una de desarrollo
        if not self.valid_keys and os.getenv('FLASK_ENV') == 'development':
            dev_key = os.getenv('DEV_API_KEY', 'dev-key-12345')
            self.valid_keys.add(dev_key)
            print(f"[WARNING] Using development API key: {dev_key}")
    
    def is_valid_key(self, api_key):
        """
        Verifica si una API key es válida
        
        Args:
            api_key: API key a validar
            
        Returns:
            bool: True si es válida, False si no
        """
        if not api_key:
            return False
        return api_key in self.valid_keys
    
    def get_api_key_from_request(self):
        """
        Extrae la API key del request actual.
        Busca en headers (X-API-Key) o query params (api_key)
        
        Returns:
            str: API key o None
        """
        # Buscar en headers
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return api_key
        
        # Buscar en query params
        api_key = request.args.get('api_key')
        if api_key:
            return api_key
        
        return None
    
    def require_api_key(self, f):
        """
        Decorador para requerir autenticación con API key en un endpoint
        
        Uso:
            @app.route('/protected')
            @auth.require_api_key
            def protected_endpoint():
                return {'message': 'Success'}
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Si auth está deshabilitada, permitir acceso
            if not self.enabled:
                return f(*args, **kwargs)
            
            # Obtener API key del request
            api_key = self.get_api_key_from_request()
            
            # Validar
            if not api_key:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'API key is missing. Provide it via X-API-Key header or api_key query parameter.'
                }), 401
            
            if not self.is_valid_key(api_key):
                return jsonify({
                    'error': 'Invalid API key',
                    'message': 'The provided API key is invalid.'
                }), 403
            
            # API key válida, continuar
            return f(*args, **kwargs)
        
        return decorated_function


def generate_api_key():
    """
    Genera una API key segura aleatoria
    
    Returns:
        str: API key de 32 caracteres
    """
    return secrets.token_urlsafe(32)


# Instancia global
auth = APIKeyAuth()
