import pytest
from src.auth import APIKeyAuth, auth

class TestAuth:
    def test_auth_instance(self):
        assert isinstance(auth, APIKeyAuth)
