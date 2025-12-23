import pytest
from unittest.mock import MagicMock, patch
from src.routes import convert_file
from src.tasks import convert_task

@pytest.fixture
def client(mocker):
    # Ensure config env is testing
    with patch('src.config.settings.ENV', 'testing'):
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        return app.test_client()

@patch('src.routes.convert_task.delay')
@patch('src.routes.scan_file')
def test_async_conversion_endpoint(mock_scan, mock_delay, client):
    # Setup mock for Celery task
    mock_task = MagicMock()
    mock_task.id = '12345'
    mock_delay.return_value = mock_task

    # Mock scan_file to pass
    mock_scan.return_value = True

    # Prepare file
    # In Flask Test Client, 'file' key in data dict should be (BytesIO, filename)
    from io import BytesIO
    data = {
        'format': 'pdf',
        'file': (BytesIO(b'fake file content'), 'test.docx')
    }

    # Make request
    response = client.post('/convert', data=data, content_type='multipart/form-data')

    # Assertions
    assert response.status_code == 202
    assert response.json['success'] == True
    assert response.json['job_id'] == '12345'
    assert response.json['status'] == 'PENDING'

    # Verify Celery was called
    mock_delay.assert_called_once()

    # Verify Scan was called
    mock_scan.assert_called_once()

@patch('src.routes.AsyncResult')
def test_status_endpoint(mock_async_result, client):
    # Mock Pending
    mock_task = MagicMock()
    mock_task.state = 'PENDING'
    mock_async_result.return_value = mock_task

    response = client.get('/status/12345')
    assert response.status_code == 200
    assert response.json['state'] == 'PENDING'

    # Mock Success
    mock_task.state = 'SUCCESS'
    mock_task.result = {'download_url': '/download/test.pdf'}
    response = client.get('/status/12345')
    assert response.status_code == 200
    assert response.json['result']['download_url'] == '/download/test.pdf'
