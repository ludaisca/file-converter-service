import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from app import create_app
from src.config import Settings


@pytest.fixture(scope='session')
def test_config():
    return Settings(
        ENV='testing',
        DEBUG=True,
        LOG_LEVEL='DEBUG',
        HOST='127.0.0.1',
        PORT=5000,
        WORKERS=1,
        ENABLE_OCR=False,
        RATE_LIMIT_ENABLED=False,
        ENABLE_CACHE=False,
    )

@pytest.fixture(scope='session')
def app(test_config):
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def temp_upload_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def temp_convert_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_text_file(temp_upload_dir):
    filepath = temp_upload_dir / 'sample.txt'
    filepath.write_text('Sample text file for testing', encoding='utf-8')
    return filepath

@pytest.fixture
def sample_pdf_file(temp_upload_dir):
    filepath = temp_upload_dir / 'sample.pdf'
    pdf_content = b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj xref 0 4 0000000000 65535 f 0000000010 00000 n 0000000063 00000 n 0000000122 00000 n trailer<</Size 4/Root 1 0 R>>startxref 214 %%EOF'
    filepath.write_bytes(pdf_content)
    return filepath

@pytest.fixture
def large_file(temp_upload_dir):
    filepath = temp_upload_dir / 'large_file.bin'
    size_bytes = 600 * 1024 * 1024
    with open(filepath, 'wb') as f:
        f.write(b'0' * size_bytes)
    return filepath

@pytest.fixture
def mock_converter_result():
    return {
        'success': True,
        'output_file': '/tmp/converted/file.pdf',
        'conversion_time_seconds': 2.5
    }

@pytest.fixture
def mock_converter_error():
    return {
        'success': False,
        'error': 'Unsupported format conversion'
    }

def get_test_data_path():
    return Path(__file__).parent / 'fixtures'

def create_json_response(success=True, error_code=None, message=None):
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat()
    }
    if error_code:
        response['error_code'] = error_code
    if message:
        response['error'] = message
    return response
