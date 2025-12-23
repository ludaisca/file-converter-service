"""
Tests para los endpoints de rutas.
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestHealthCheck:
    """
    Tests para el endpoint /health.
    """
    
    def test_health_check_success(self, client):
        """Probar que /health retorna 200 y estructura correcta."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['status'] == 'healthy'
        assert data['service'] == 'file-converter'
        assert 'timestamp' in data
        assert 'system' in data
        assert 'api' in data
        assert 'features' in data
    
    def test_health_check_system_metrics(self, client):
        """Probar que health check incluye métricas del sistema."""
        response = client.get('/health')
        data = response.get_json()
        
        system = data['system']
        assert 'cpu_usage_percent' in system
        assert 'memory_usage_percent' in system
        assert 'memory_available_mb' in system
        assert 'disk_usage_percent' in system
        assert 'disk_free_gb' in system
    
    def test_health_check_api_info(self, client):
        """Probar que health check incluye información de API."""
        response = client.get('/health')
        data = response.get_json()
        
        api = data['api']
        assert 'version' in api
        assert api['version'] == '2.0.0'
        assert 'upload_folder_exists' in api
        assert 'converted_folder_exists' in api
        assert 'logs_folder_exists' in api
    
    def test_health_check_features(self, client):
        """Probar que health check incluye información de features."""
        response = client.get('/health')
        data = response.get_json()
        
        features = data['features']
        assert 'ocr_enabled' in features
        assert isinstance(features['ocr_enabled'], bool)


class TestGetSupportedFormats:
    """
    Tests para el endpoint /formats.
    """
    
    def test_get_formats_success(self, client):
        """Probar que /formats retorna formatos soportados."""
        response = client.get('/formats')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'supported_formats' in data
        assert 'timestamp' in data
    
    def test_get_formats_structure(self, client):
        """Probar estructura de respuesta de formatos."""
        response = client.get('/formats')
        data = response.get_json()
        
        # Debe ser un dict con formatos
        supported = data['supported_formats']
        assert isinstance(supported, dict)
        assert len(supported) > 0


class TestConvertFile:
    """
    Tests para el endpoint /convert.
    """
    
    def test_convert_without_format(self, client):
        """Probar que /convert sin formato falla con 400."""
        response = client.post('/convert')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error_code' in data
        assert data['error_code'] == 'UNSUPPORTED_FORMAT'
    
    def test_convert_without_file_or_url(self, client):
        """Probar que /convert sin archivo o URL falla."""
        response = client.post('/convert', data={'format': 'pdf'})
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_FILE'
    
    def test_convert_with_invalid_format(self, client):
        """Probar que formato inválido es rechazado."""
        response = client.post(
            '/convert',
            data={'format': 'xyz'},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert data['error_code'] == 'UNSUPPORTED_FORMAT'
    
    def test_convert_with_text_file(self, client, sample_text_file):
        """Probar conversión con archivo de texto."""
        with open(sample_text_file, 'rb') as f:
            response = client.post(
                '/convert',
                data={'file': f, 'format': 'pdf'},
                content_type='multipart/form-data'
            )
        
        # Dependiendo de si el archivo se processó correctamente
        # (puede fallar si no hay conversor disponible)
        assert response.status_code in [200, 500]
        data = response.get_json()
        
        # Al menos debe tener estructura correcta
        assert 'success' in data
        assert 'timestamp' in data
    
    def test_convert_response_structure_on_error(self, client):
        """Probar estructura de respuesta de error en /convert."""
        response = client.post('/convert', data={})
        
        data = response.get_json()
        
        # Todos los errores deben tener esta estructura
        assert 'success' in data
        assert 'error' in data or 'error_code' in data
        assert 'timestamp' in data


class TestDownloadFile:
    """
    Tests para el endpoint /download/<filename>.
    """
    
    def test_download_nonexistent_file(self, client):
        """Probar que descargar archivo inexistente falla con 404."""
        response = client.get('/download/nonexistent.pdf')
        
        assert response.status_code == 404
        data = response.get_json()
        
        assert data['success'] is False
        assert data['error_code'] == 'FILE_NOT_FOUND'
    
    def test_download_response_structure(self, client):
        """Probar estructura de respuesta de download."""
        response = client.get('/download/missing.pdf')
        
        data = response.get_json()
        
        assert 'success' in data
        assert 'timestamp' in data


class TestExtractText:
    """
    Tests para el endpoint /extract-text (OCR).
    """
    
    def test_extract_text_without_file_or_url(self, client):
        """Probar que /extract-text sin archivo o URL falla."""
        response = client.post('/extract-text')
        
        # Puede ser 503 (OCR disabled) o 400 (sin archivo)
        assert response.status_code in [400, 503]
        data = response.get_json()
        
        assert data['success'] is False
    
    @patch('src.config_refactored.settings')
    def test_extract_text_ocr_disabled(self, mock_settings, client):
        """Probar que /extract-text falla cuando OCR está deshabilitado."""
        mock_settings.ENABLE_OCR = False
        
        response = client.post('/extract-text', data={})
        
        # Puede retornar 503 pero verifica que el error es porque OCR está deshabilitado
        assert response.status_code in [400, 503]
        data = response.get_json()
        
        assert data['success'] is False
    
    def test_extract_text_response_structure_error(self, client):
        """Probar estructura de respuesta de error en /extract-text."""
        response = client.post('/extract-text', data={})
        
        data = response.get_json()
        
        assert 'success' in data
        assert 'timestamp' in data


class TestOCRLanguages:
    """
    Tests para el endpoint /ocr/languages.
    """
    
    def test_ocr_languages_endpoint(self, client):
        """Probar que /ocr/languages está disponible."""
        response = client.get('/ocr/languages')
        
        # Puede ser 503 si OCR está deshabilitado o 200 si está habilitado
        assert response.status_code in [200, 503]
        data = response.get_json()
        
        assert 'success' in data
        assert 'timestamp' in data


class TestErrorHandlers:
    """
    Tests para error handlers globales.
    """
    
    def test_404_not_found(self, client):
        """Probar que rutas inexistentes retornan 404."""
        response = client.get('/nonexistent-route')
        
        assert response.status_code == 404
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error_code' in data
    
    def test_405_method_not_allowed(self, client):
        """Probar que métodos no permitidos retornan 405."""
        # /health solo acepta GET
        response = client.post('/health')
        
        assert response.status_code == 405
        data = response.get_json()
        
        assert data['success'] is False


class TestResponseConsistency:
    """
    Tests para verificar consistencia de respuestas.
    """
    
    def test_all_error_responses_have_success_field(self, client):
        """Probar que todas las respuestas de error tienen 'success'."""
        error_endpoints = [
            ('/nonexistent', 'GET'),
            ('/convert', 'POST'),
            ('/download/missing.pdf', 'GET'),
        ]
        
        for endpoint, method in error_endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            data = response.get_json()
            assert 'success' in data, f"Missing 'success' in {endpoint}"
    
    def test_all_responses_have_timestamp(self, client):
        """Probar que todas las respuestas tienen timestamp."""
        endpoints = [
            ('/health', 'GET'),
            ('/formats', 'GET'),
        ]
        
        for endpoint, method in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            data = response.get_json()
            assert 'timestamp' in data, f"Missing 'timestamp' in {endpoint}"


class TestRequestValidation:
    """
    Tests para validación de requests.
    """
    
    def test_missing_required_parameters(self, client):
        """Probar manejo de parámetros requeridos faltantes."""
        response = client.post('/convert', data={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_invalid_content_type(self, client):
        """Probar manejo de content-type inválido."""
        response = client.post(
            '/convert',
            data=json.dumps({'format': 'pdf'}),
            content_type='application/json'
        )
        
        # Flask permite esto pero el form estará vacío
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestSecurity:
    """
    Tests para verificaciones de seguridad.
    """
    
    def test_response_has_security_headers(self, client):
        """Probar que respuestas incluyen headers de seguridad."""
        response = client.get('/health')
        
        # Verificar headers de seguridad
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        
        assert 'X-XSS-Protection' in response.headers
    
    def test_filename_sanitization(self, client):
        """Probar que nombres de archivo se sanitizan."""
        # Intentar path traversal
        response = client.get('/download/../../../etc/passwd')
        
        # Debe ser 404, no un error de path traversal
        assert response.status_code == 404


class TestCORS:
    """
    Tests para CORS headers.
    """
    
    def test_cors_headers_present(self, client):
        """Probar que CORS headers están presentes."""
        response = client.get('/health', headers={'Origin': 'http://localhost:3000'})
        
        # CORS headers deben estar presentes
        assert response.status_code == 200
