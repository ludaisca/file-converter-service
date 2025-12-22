import pytest
import sys
import os
from pathlib import Path

# Add the application root directory to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['UPLOAD_FOLDER'] = '/tmp/uploads_test'
    flask_app.config['CONVERTED_FOLDER'] = '/tmp/converted_test'

    # Patch the global variables in app.py to use test folders
    import app as app_module

    # Store original values
    orig_upload = app_module.UPLOAD_FOLDER
    orig_converted = app_module.CONVERTED_FOLDER

    # Set new values
    app_module.UPLOAD_FOLDER = flask_app.config['UPLOAD_FOLDER']
    app_module.CONVERTED_FOLDER = flask_app.config['CONVERTED_FOLDER']

    # Create test directories
    os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(flask_app.config['CONVERTED_FOLDER'], exist_ok=True)

    yield flask_app

    # Restore original values
    app_module.UPLOAD_FOLDER = orig_upload
    app_module.CONVERTED_FOLDER = orig_converted

    # Clean up (optional, as OS handles /tmp usually, but good practice)
    # import shutil
    # shutil.rmtree(flask_app.config['UPLOAD_FOLDER'])
    # shutil.rmtree(flask_app.config['CONVERTED_FOLDER'])

@pytest.fixture
def client(app):
    return app.test_client()
