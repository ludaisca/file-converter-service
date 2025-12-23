"""
Tests para Rate Limiter (src/rate_limiter.py).
"""
import pytest
from unittest.mock import MagicMock, patch
from src.rate_limiter import get_rate_limit_key, init_limiter

class TestRateLimiter:

    def test_get_rate_limit_key_api_key(self):
        """Probar key basada en API Key."""
        with patch('flask.request', MagicMock()) as mock_request:
            mock_request.headers.get.return_value = 'my-secret-key'
            key = get_rate_limit_key()
            assert key == 'api_key:my-secret-key'

    @patch('src.rate_limiter.get_remote_address')
    def test_get_rate_limit_key_ip(self, mock_addr):
        """Probar key basada en IP si no hay API Key."""
        with patch('flask.request', MagicMock()) as mock_request:
            mock_request.headers.get.return_value = None
            mock_addr.return_value = '127.0.0.1'

            key = get_rate_limit_key()
            assert key == 'ip:127.0.0.1'

    def test_init_limiter(self):
        """Probar inicialización del limiter."""
        app_mock = MagicMock()

        limiter = init_limiter(app_mock)

        assert limiter is not None
        # Verificar que se registró el error handler
        app_mock.errorhandler.assert_called_with(429)
