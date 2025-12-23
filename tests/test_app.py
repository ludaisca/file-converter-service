"""
Tests para app.py y factory pattern.
"""

import pytest
from unittest.mock import patch, MagicMock
from app import create_app


class TestCreateAppFactory:
    """
    Tests para la factory function create_app().
    """
    
    def test_create_app_returns_flask_app(self):
        """Probar que create_app() retorna una instancia Flask."""
        app = create_app()
        
        assert app is not None
        assert hasattr(app, 'route')
        assert hasattr(app, 'run')
        assert hasattr(app, 'test_client')
    
    def test_create_app_routes_registered(self):
        """Probar que las rutas están registradas."""
        app = create_app()
        client = app.test_client()
        
        # Verificar que algunas rutas están disponibles
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_create_app_error_handlers(self):
        """Probar que error handlers están registrados."""
        app = create_app()
        
        # Verificar que error handlers existen
        assert len(app.error_handler_spec) > 0 or len(app.error_handler_spec.get(None, {})) > 0


class TestAppConfiguration:
    """
    Tests para configuración de la app.
    """
    
    def test_app_config_type(self, app):
        """Probar que app tiene config."""
        assert app.config is not None
        assert isinstance(app.config, dict)
    
    def test_app_has_logger(self, app):
        """Probar que app tiene logger."""
        assert app.logger is not None


class TestAppStartup:
    """
    Tests para startup de la app.
    """
    
    def test_app_startup_succeeds(self):
        """Probar que la app inicia sin errores."""
        try:
            app = create_app()
            assert app is not None
        except Exception as e:
            pytest.fail(f"App startup failed: {e}")
    
    def test_app_context_available(self):
        """Probar que app context está disponible."""
        app = create_app()
        
        with app.app_context():
            assert app.name is not None


class TestAppRoutes:
    """
    Tests para disponibilidad de rutas.
    """
    
    def test_health_route_available(self, client):
        """Probar que ruta /health está disponible."""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_formats_route_available(self, client):
        """Probar que ruta /formats está disponible."""
        response = client.get('/formats')
        assert response.status_code == 200
    
    def test_convert_route_available(self, client):
        """Probar que ruta /convert está disponible."""
        response = client.post('/convert', data={})
        # Puede ser 400 (sin datos) pero la ruta debe existir
        assert response.status_code in [400, 500]


class TestAppResponseFormat:
    """
    Tests para formato de respuestas.
    """
    
    def test_all_responses_are_json(self, client):
        """Probar que todas las respuestas son JSON."""
        endpoints = [
            ('/health', 'GET'),
            ('/formats', 'GET'),
        ]
        
        for endpoint, method in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            assert response.content_type == 'application/json'
            assert response.get_json() is not None
    
    def test_error_responses_have_error_field(self, client):
        """Probar que respuestas de error tienen 'error' o 'error_code'."""
        response = client.get('/nonexistent')
        
        assert response.status_code == 404
        data = response.get_json()
        
        assert 'error' in data or 'error_code' in data


class TestAppLogging:
    """
    Tests para logging de la app.
    """
    
    def test_app_logger_exists(self, app):
        """Probar que logger de app existe."""
        assert app.logger is not None
        assert hasattr(app.logger, 'info')
        assert hasattr(app.logger, 'error')
    
    def test_app_logger_can_log(self, app):
        """Probar que logger puede escribir."""
        try:
            app.logger.info("Test message")
            app.logger.error("Error message")
            assert True
        except Exception as e:
            pytest.fail(f"Logging failed: {e}")


class TestAppTesting:
    """
    Tests para modo testing de la app.
    """
    
    def test_app_testing_mode(self):
        """Probar que app puede iniciar en modo testing."""
        app = create_app()
        app.config['TESTING'] = True
        
        assert app.test_client() is not None
    
    def test_app_test_client_works(self):
        """Probar que test client funciona."""
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        response = client.get('/health')
        assert response.status_code == 200


class TestAppIntegration:
    """
    Tests de integración de app.
    """
    
    def test_full_request_response_cycle(self, client):
        """Probar ciclo completo de request-response."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'success' in data
        assert 'timestamp' in data
        assert data['success'] is True
    
    def test_error_request_response_cycle(self, client):
        """Probar ciclo de error en request-response."""
        response = client.get('/nonexistent')
        
        assert response.status_code == 404
        data = response.get_json()
        
        assert 'success' in data
        assert data['success'] is False
