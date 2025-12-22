from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
import requests
from pathlib import Path
import threading
import time
import json
import logging
import psutil
from datetime import datetime
from functools import wraps
import gzip
import io

# Configure structured logging
log_dir = '/app/logs'
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir, exist_ok=True)
    except PermissionError:
        # Fallback for local testing or restricted environments
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, 'app.log'), mode='a')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = '/app/uploads'
CONVERTED_FOLDER = '/app/converted'
LOGS_FOLDER = '/app/logs'
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50)) * 1024 * 1024
MAX_DOWNLOAD_SIZE = int(os.getenv('MAX_DOWNLOAD_SIZE', 100)) * 1024 * 1024
CLEANUP_INTERVAL = int(os.getenv('CLEANUP_INTERVAL', 3600))
FILE_TTL = int(os.getenv('FILE_TTL', 3600))

# Formatos soportados
SUPPORTED_CONVERSIONS = {
    'document': {
        'from': ['.docx', '.doc', '.odt', '.rtf', '.txt'],
        'to': ['.pdf', '.docx', '.txt', '.html']
    },
    'image': {
        'from': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
        'to': ['.jpg', '.png', '.pdf', '.webp']
    },
    'video': {
        'from': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'],
        'to': ['.mp4', '.avi', '.gif']
    },
    'audio': {
        'from': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
        'to': ['.mp3', '.wav', '.ogg']
    }
}

# Middleware for gzip compression
def gzip_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        rv = f(*args, **kwargs)
        if isinstance(rv, tuple):
            response_data, status_code = rv[0], rv[1]
        else:
            response_data = rv
            status_code = 200
        
        if request.accept_encodings.get('gzip'):
            if isinstance(response_data, str):
                compressed = gzip.compress(response_data.encode('utf-8'))
                return compressed, status_code, {'Content-Encoding': 'gzip', 'Content-Type': 'application/json'}
        
        return rv
    return decorated_function

def download_file_from_url(url: str, upload_folder: Path) -> Path:
    logger.info(f"Downloading file from URL: {url}")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        original_name = url.split('/')[-1] or 'downloaded_file'
        name, ext = os.path.splitext(original_name)
        
        safe_name = secure_filename(name) or 'file'
        unique_name = f"{uuid.uuid4().hex}_{safe_name}{ext}"
        file_path = upload_folder / unique_name
        
        size = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    size += len(chunk)
                    if size > MAX_DOWNLOAD_SIZE:
                        file_path.unlink()
                        logger.error(f"Downloaded file exceeds maximum size")
                        raise ValueError(f'Downloaded file exceeds maximum size of {MAX_DOWNLOAD_SIZE / (1024*1024):.0f}MB')
                    f.write(chunk)
        
        logger.info(f"Successfully downloaded file: {unique_name} ({size} bytes)")
        return file_path
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading file from URL: {str(e)}")
        raise ValueError(f'Error downloading file from URL: {str(e)}')
    except Exception as e:
        logger.error(f"Error processing downloaded file: {str(e)}")
        raise ValueError(f'Error processing downloaded file: {str(e)}')

def cleanup_files():
    """Background task to clean up old files."""
    logger.info("Starting cleanup thread...")
    while True:
        try:
            now = time.time()
            for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:
                if not os.path.exists(folder):
                    continue
                for f in os.listdir(folder):
                    f_path = os.path.join(folder, f)
                    try:
                        if os.path.isfile(f_path):
                            if os.stat(f_path).st_mtime < now - FILE_TTL:
                                os.remove(f_path)
                                logger.debug(f"Deleted old file: {f}")
                    except Exception as e:
                        logger.debug(f"Error processing {f_path}: {e}")
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")
        time.sleep(CLEANUP_INTERVAL)

@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    try:
        disk_usage = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        
        health_data = {
            'status': 'healthy',
            'service': 'file-converter',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': time.time(),
            'system': {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory_info.percent,
                'memory_available_mb': memory_info.available / (1024 * 1024),
                'disk_usage_percent': disk_usage.percent,
                'disk_free_gb': disk_usage.free / (1024 ** 3)
            },
            'api': {
                'version': '1.0.0',
                'upload_folder_exists': os.path.exists(UPLOAD_FOLDER),
                'converted_folder_exists': os.path.exists(CONVERTED_FOLDER),
                'logs_folder_exists': os.path.exists(LOGS_FOLDER)
            }
        }
        
        logger.info("Health check performed successfully")
        return jsonify(health_data), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/formats', methods=['GET'])
def get_supported_formats():
    """Get supported conversion formats."""
    logger.info("Requested supported formats")
    return jsonify(SUPPORTED_CONVERSIONS)

@app.route('/convert', methods=['POST'])
def convert_file():
    try:
        target_format = request.form.get('format', '').lower()
        
        if not target_format:
            logger.warning("Convert request without target format")
            return jsonify({'error': 'Target format not specified'}), 400
        
        upload_folder = Path(UPLOAD_FOLDER)
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        source_path = None
        
        # 1) Archivo subido
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            source_path = upload_folder / unique_name
            file.save(source_path)
            logger.info(f"File uploaded: {unique_name}")
        
        # 2) URL remota
        elif 'url' in request.form:
            url = request.form.get('url', '').strip()
            if not url:
                return jsonify({'error': 'Empty URL provided'}), 400
            try:
                source_path = download_file_from_url(url, upload_folder)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        
        else:
            logger.warning("Convert request without file or URL")
            return jsonify({'error': 'Provide either "file" or "url"'}), 400
        
        # Validar tamaño del archivo
        if source_path.stat().st_size > MAX_FILE_SIZE:
            source_path.unlink()
            logger.warning(f"File too large: {source_path.stat().st_size} bytes")
            return jsonify({'error': f'File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB'}), 413
        
        # Convertir archivo
        original_ext = source_path.suffix.lower()
        target_ext = f".{target_format}" if not target_format.startswith('.') else target_format
        file_id = source_path.stem.split('_')[0]
        output_filename = f"{file_id}{target_ext}"
        output_path = Path(CONVERTED_FOLDER) / output_filename
        
        logger.info(f"Converting {original_ext} to {target_ext} (ID: {file_id})")
        
        conversion_result = perform_conversion(str(source_path), str(output_path), original_ext, target_ext)
        
        if not conversion_result['success']:
            if source_path.exists():
                source_path.unlink()
            logger.error(f"Conversion failed: {conversion_result['error']}")
            return jsonify({'error': conversion_result['error']}), 500
        
        # Limpiar archivo original
        if source_path.exists():
            source_path.unlink()
        
        logger.info(f"Conversion completed successfully (ID: {file_id})")
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'output_format': target_format,
            'download_url': f'/download/{output_filename}'
        })
    
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(CONVERTED_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            logger.info(f"File downloaded: {filename}")
            return send_file(file_path, as_attachment=True)
        logger.warning(f"File not found: {filename}")
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def perform_conversion(input_path, output_path, from_ext, to_ext):
    try:
        # LibreOffice conversions
        if from_ext in ['.docx', '.doc', '.odt', '.rtf'] and to_ext == '.pdf':
            subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'pdf',
                '--outdir', CONVERTED_FOLDER, input_path
            ], check=True)
            return {'success': True}
        
        # ImageMagick
        elif from_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'] and to_ext in ['.jpg', '.png', '.pdf', '.webp']:
            subprocess.run([
                'convert', input_path, output_path
            ], check=True)
            return {'success': True}
        
        # Video con FFmpeg
        elif from_ext in ['.mp4', '.avi', '.mov', '.mkv'] and to_ext in ['.mp4', '.avi', '.gif']:
            subprocess.run([
                'ffmpeg', '-i', input_path, '-y', output_path
            ], check=True)
            return {'success': True}
        
        # Audio con FFmpeg
        elif from_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac'] and to_ext in ['.mp3', '.wav', '.ogg']:
            subprocess.run([
                'ffmpeg', '-i', input_path, '-y', output_path
            ], check=True)
            return {'success': True}
        
        else:
            return {'success': False, 'error': 'Conversion not supported'}
        
    except subprocess.CalledProcessError as e:
        return {'success': False, 'error': f'Conversion failed: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CONVERTED_FOLDER, exist_ok=True)
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    
    cleanup_thread = threading.Thread(target=cleanup_files, daemon=True)
    cleanup_thread.start()
    
    logger.info("Starting file-converter service...")
    app.run(host='0.0.0.0', port=5000, debug=False)
