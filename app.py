from flask import Flask
import threading
from src.config import Config
from src.logging import logger
from src.utils import cleanup_files
from src.routes import main_bp

def create_app():
    app = Flask(__name__)
    Config.init_app(app)
    
    app.register_blueprint(main_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    
    cleanup_thread = threading.Thread(target=cleanup_files, daemon=True)
    cleanup_thread.start()
    
    logger.info("Starting file-converter service...")
    app.run(host='0.0.0.0', port=5000, debug=False)
