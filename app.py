import os
import sys
import threading
import time
import logging
import signal
from pathlib import Path
from flask import Flask
from flasgger import Swagger
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from src.config import Config, settings
from src.routes import register_routes
from src.logging import setup_logging
from src.metrics import CONVERSION_DURATION, FILES_PROCESSED, CONVERSION_ERRORS

def create_app(config_class=Config):
    if not hasattr(create_app, 'logging_setup'):
         os.makedirs(settings.LOGS_FOLDER, exist_ok=True)
         setup_logging()
         create_app.logging_setup = True

    logger = logging.getLogger('file_converter')
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    # Initialize Swagger
    swagger = Swagger(app)

    # Initialize Prometheus Metrics for Flask HTTP requests
    if settings.ENV != 'testing':
        metrics = PrometheusMetrics(app)
        metrics.info('app_info', 'Application info', version=settings.API_VERSION)

    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(settings.CONVERTED_FOLDER, exist_ok=True)

    register_routes(app)

    logger.info("Application initialized successfully")
    return app

def cleanup_thread(app):
    logger = logging.getLogger('file_converter')
    while True:
        try:
            time.sleep(300)
            now = time.time()
            ttl = settings.MAX_UPLOAD_TIMEOUT if hasattr(settings, 'MAX_UPLOAD_TIMEOUT') else 3600

            for folder in [settings.UPLOAD_FOLDER, settings.CONVERTED_FOLDER]:
                if not folder.exists():
                    continue
                for item in folder.iterdir():
                    if item.is_file():
                        if item.stat().st_mtime < now - ttl:
                            try:
                                item.unlink()
                                logger.info(f"Cleaned up old file: {item}")
                            except Exception as e:
                                logger.error(f"Failed to delete {item}: {e}")
        except Exception as e:
            logger.error(f"Error in cleanup thread: {e}")

def main():
    app = create_app()
    cleaner = threading.Thread(target=cleanup_thread, args=(app,), daemon=True)
    cleaner.start()
    def signal_handler(sig, frame):
        logging.getLogger('file_converter').info("Shutting down...")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
