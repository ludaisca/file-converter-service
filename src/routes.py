from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from pathlib import Path
import psutil
import time
from datetime import datetime
from .config import Config
from .logging import logger
from .utils import gzip_response, download_file_from_url
from .converters.factory import ConverterFactory

main_bp = Blueprint('main', __name__)
converter_factory = ConverterFactory()

@main_bp.route('/health', methods=['GET'])
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
                'upload_folder_exists': os.path.exists(Config.UPLOAD_FOLDER),
                'converted_folder_exists': os.path.exists(Config.CONVERTED_FOLDER),
                'logs_folder_exists': os.path.exists(Config.LOGS_FOLDER)
            }
        }

        logger.info("Health check performed successfully")
        return jsonify(health_data), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@main_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """Get supported conversion formats."""
    logger.info("Requested supported formats")
    return jsonify(Config.SUPPORTED_CONVERSIONS)

@main_bp.route('/convert', methods=['POST'])
def convert_file():
    try:
        target_format = request.form.get('format', '').lower()

        if not target_format:
            logger.warning("Convert request without target format")
            return jsonify({'error': 'Target format not specified'}), 400

        upload_folder = Path(Config.UPLOAD_FOLDER)

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
        if source_path.stat().st_size > Config.MAX_FILE_SIZE:
            source_path.unlink()
            logger.warning(f"File too large: {source_path.stat().st_size} bytes")
            return jsonify({'error': f'File too large. Maximum size is {Config.MAX_FILE_SIZE / (1024*1024):.0f}MB'}), 413

        # Convertir archivo
        original_ext = source_path.suffix.lower()
        target_ext = f".{target_format}" if not target_format.startswith('.') else target_format
        file_id = source_path.stem.split('_')[0]
        output_filename = f"{file_id}{target_ext}"
        output_path = Path(Config.CONVERTED_FOLDER) / output_filename

        logger.info(f"Converting {original_ext} to {target_ext} (ID: {file_id})")

        conversion_result = converter_factory.perform_conversion(str(source_path), str(output_path), original_ext, target_ext)

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

@main_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(Config.CONVERTED_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            logger.info(f"File downloaded: {filename}")
            return send_file(file_path, as_attachment=True)
        logger.warning(f"File not found: {filename}")
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500
