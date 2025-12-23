from flask import Flask, jsonify
from datetime import datetime
import threading
from src.config import Config
from src.logging import logger
from src.utils import cleanup_files
from src.routes import main_bp

def create_app():
    app = Flask(__name__)
    Config.init_app(app)
    
    app.register_blueprint(main_bp)
    
    # Root route - API info
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint - returns API information."""
        return jsonify({
            'success': True,
            'service': 'file-converter-service',
            'version': '2.0.0',
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'health': '/health',
                'formats': '/formats',
                'convert': '/convert',
                'extract_text': '/extract-text',
                'ocr_languages': '/ocr/languages'
            },
            'documentation': {
                'github': 'https://github.com/ludaisca/file-converter-service',
                'api_docs': '/health',
                'issues': 'https://github.com/ludaisca/file-converter-service/issues'
            }
        }), 200

    return app

if __name__ == '__main__':
    app = create_app()
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_files, daemon=True)
    cleanup_thread.start()
    
    logger.info("Starting file-converter service...")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
