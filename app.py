import os
import sys
import threading
import time
import logging
import signal
from pathlib import Path
from flask import Flask
from flask_compress import Compress

from src.config import Config, settings
from src.routes import register_routes
from src.logging import setup_logging
from src.rate_limiter import init_limiter
from src.async_worker import async_manager
from src.cache_manager import get_cache

def create_app(config_class=Config):
    """Application factory pattern for Flask app creation.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    # Ensure directories exist
    os.makedirs(settings.LOGS_FOLDER, exist_ok=True)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger('file_converter')

    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable gzip compression for responses
    Compress(app)
    app.config['COMPRESS_MIMETYPES'] = [
        'application/json',
        'text/html',
        'text/xml',
        'application/xml'
    ]
    app.config['COMPRESS_LEVEL'] = 6
    app.config['COMPRESS_MIN_SIZE'] = 500
    
    # Initialize Rate Limiting
    init_limiter(app)

    # Ensure upload/conversion directories exist
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(settings.CONVERTED_FOLDER, exist_ok=True)
    os.makedirs(settings.TEMP_FOLDER, exist_ok=True)
    
    # Initialize cache (will auto-detect if Redis is available)
    cache = get_cache()
    cache_health = cache.health_check()
    if cache_health['healthy']:
        logger.info("Cache initialized successfully")
    else:
        logger.warning(f"Cache initialization: {cache_health['message']}")

    # Register routes
    register_routes(app)

    logger.info(f"Application initialized successfully (ENV: {settings.ENV})")
    logger.info(f"Workers configured: {settings.WORKERS}")
    logger.info(f"Cache enabled: {settings.ENABLE_CACHE}")
    
    return app

def cleanup_thread(app):
    """Background thread for cleaning up old temporary files.
    
    Args:
        app: Flask application instance
    """
    logger = logging.getLogger('file_converter')
    logger.info("Cleanup thread started")
    
    while True:
        try:
            time.sleep(300)  # Run every 5 minutes
            now = time.time()
            ttl = settings.MAX_UPLOAD_TIMEOUT if hasattr(settings, 'MAX_UPLOAD_TIMEOUT') else 3600

            for folder in [settings.UPLOAD_FOLDER, settings.CONVERTED_FOLDER, settings.TEMP_FOLDER]:
                if not folder.exists():
                    continue
                    
                cleaned_count = 0
                for item in folder.iterdir():
                    if item.is_file():
                        if item.stat().st_mtime < now - ttl:
                            try:
                                item.unlink()
                                cleaned_count += 1
                            except Exception as e:
                                logger.error(f"Failed to delete {item}: {e}")
                
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} old files from {folder.name}")
                    
        except Exception as e:
            logger.error(f"Error in cleanup thread: {e}", exc_info=True)

# Create the app instance (used by Gunicorn)
app = create_app()

# Start async worker when app is created
@app.before_first_request
def start_workers():
    """Start background workers on first request."""
    async_manager.start()
    logger = logging.getLogger('file_converter')
    logger.info("Async worker manager started")

def main():
    """Main function for running development server.
    
    This is used when running directly with `python app.py`.
    For production, use Gunicorn instead.
    """
    logger = logging.getLogger('file_converter')
    logger.warning("Running Flask development server. Use Gunicorn for production!")
    
    # Start async worker
    async_manager.start()
    
    # Start cleanup thread
    cleaner = threading.Thread(target=cleanup_thread, args=(app,), daemon=True)
    cleaner.start()
    logger.info("Cleanup thread started")
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info("Shutting down gracefully...")
        async_manager.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run development server
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting development server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=settings.DEBUG)

if __name__ == '__main__':
    main()
