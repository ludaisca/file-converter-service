"""
Configuración compartida de fixtures para todos los tests.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from app_refactored import create_app
from src.config_refactored import Settings


@pytest.fixture(scope='session')
def test_config():
    """
    Configuración para tests (testing environment).
    
    Returns:
        Settings: Configuración con valores seguros para testing
    """
    return Settings(
        ENV='testing',
        DEBUG=True,
        LOG_LEVEL='DEBUG',
        HOST='127.0.0.1',
        PORT=5000,
        WORKERS=1,
        ENABLE_OCR=False,  # Deshabilitar OCR en tests
        RATE_LIMIT_ENABLED=False,  # Deshabilitar rate limit en tests
        ENABLE_CACHE=False,  # Deshabilitar cache en tests
    )


@pytest.fixture(scope='session')
def app(test_config):
    """
    Crear aplicación Flask para tests.
    
    Args:
        test_config: Configuración de testing
    
    Returns:
        Flask: Aplicación configurada para testing
    """
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """
    Cliente de prueba para hacer requests a la aplicación.
    
    Args:
        app: Aplicación Flask
    
    Returns:
        FlaskClient: Cliente para hacer requests
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    CLI runner para probar comandos CLI.
    
    Args:
        app: Aplicación Flask
    
    Returns:
        CliRunner: Runner de CLI
    """
    return app.test_cli_runner()


@pytest.fixture
def temp_upload_dir():
    """
    Directorio temporal para archivos subidos durante tests.
    
    Yields:
        Path: Ruta al directorio temporal
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_convert_dir():
    """
    Directorio temporal para archivos convertidos durante tests.
    
    Yields:
        Path: Ruta al directorio temporal
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text_file(temp_upload_dir):
    """
    Crear archivo de texto de muestra para tests.
    
    Args:
        temp_upload_dir: Directorio temporal
    
    Returns:
        Path: Ruta al archivo de muestra
    """
    filepath = temp_upload_dir / 'sample.txt'
    filepath.write_text('Sample text file for testing', encoding='utf-8')
    return filepath


@pytest.fixture
def sample_pdf_file(temp_upload_dir):
    """
    Crear archivo PDF de muestra para tests.
    
    Note: Este es un PDF válido pero muy simple.
    
    Args:
        temp_upload_dir: Directorio temporal
    
    Returns:
        Path: Ruta al archivo PDF
    """
    filepath = temp_upload_dir / 'sample.pdf'
    # Mínimo PDF válido
    pdf_content = b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj xref 0 4 0000000000 65535 f 0000000010 00000 n 0000000063 00000 n 0000000122 00000 n trailer<</Size 4/Root 1 0 R>>startxref 214 %%EOF'
    filepath.write_bytes(pdf_content)
    return filepath


@pytest.fixture
def large_file(temp_upload_dir):
    """
    Crear archivo grande para tests de límite de tamaño.
    
    Crea un archivo de ~600MB (excede el límite de 500MB por defecto).
    
    Args:
        temp_upload_dir: Directorio temporal
    
    Returns:
        Path: Ruta al archivo grande
    """
    filepath = temp_upload_dir / 'large_file.bin'
    # Crear archivo de 600MB
    size_bytes = 600 * 1024 * 1024
    with open(filepath, 'wb') as f:
        f.write(b'0' * size_bytes)
    return filepath


@pytest.fixture
def mock_converter_result():
    """
    Mock de resultado de conversión exitosa.
    
    Returns:
        dict: Resultado simulado de conversión
    """
    return {
        'success': True,
        'output_file': '/tmp/converted/file.pdf',
        'conversion_time_seconds': 2.5
    }


@pytest.fixture
def mock_converter_error():
    """
    Mock de resultado de conversión fallida.
    
    Returns:
        dict: Resultado simulado de error
    """
    return {
        'success': False,
        'error': 'Unsupported format conversion'
    }


# ==================
# Utilidades de Test
# ==================

def get_test_data_path():
    """
    Obtener ruta a directorio de datos de test.
    
    Returns:
        Path: Ruta a tests/fixtures/
    """
    return Path(__file__).parent / 'fixtures'


def create_json_response(success=True, error_code=None, message=None):
    """
    Crear respuesta JSON simulada para tests.
    
    Args:
        success: Si fue exitoso
        error_code: Código de error (si aplica)
        message: Mensaje (si aplica)
    
    Returns:
        dict: Respuesta simulada
    """
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    }
    if error_code:
        response['error_code'] = error_code
    if message:
        response['error'] = message
    return response
