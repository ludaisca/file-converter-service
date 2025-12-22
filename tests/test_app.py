import unittest
import json
import os
from app import create_app
from src.config import Config

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('system', data)

    def test_formats(self):
        response = self.client.get('/formats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('document', data)
        self.assertIn('image', data)

    def test_download_not_found(self):
        response = self.client.get('/download/nonexistent.file')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
