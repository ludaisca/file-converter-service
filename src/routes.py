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
from .validators import FileValidator
from .ocr import OCRProcessor

main_bp = Blueprint('main', __name__)
converter_factory = ConverterFactory()

# Inicializar OCR processor
ocr_enabled = os.getenv('ENABLE_OCR', 'true').lower() == 'true'
ocr_processor = OCRProcessor(default_lang=os.getenv('OCR_DEFAULT_LANGUAGE', 'spa')) if ocr_enabled else None

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
            },
            'features': {
                'ocr_enabled': ocr_enabled,
                'ocr_languages': ocr_processor.get_available_languages() if ocr_processor else []
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

# ==================
# OCR Endpoints
# ==================

@main_bp.route('/extract-text', methods=['POST'])
def extract_text():
    """
    Extrae texto de imagen o PDF usando OCR.
    
    Form Parameters:
        - file: Archivo de imagen o PDF
        - url: URL de imagen o PDF (alternativa a file)
        - lang: Código de idioma (spa, eng, etc.) - opcional
        - preprocess: true/false - aplicar preprocesamiento - opcional
    """
    if not ocr_enabled:
        return jsonify({'error': 'OCR functionality is disabled'}), 503
    
    try:
        # Obtener parámetros
        lang = request.form.get('lang', os.getenv('OCR_DEFAULT_LANGUAGE', 'spa'))
        preprocess = request.form.get('preprocess', 'true').lower() == 'true'
        
        upload_folder = Path(Config.UPLOAD_FOLDER)
        source_path = None
        
        # Obtener archivo (subido o desde URL)
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            source_path = upload_folder / unique_name
            file.save(source_path)
            logger.info(f"OCR file uploaded: {unique_name}")
        
        elif 'url' in request.form:
            url = request.form.get('url', '').strip()
            if not url:
                return jsonify({'error': 'Empty URL provided'}), 400
            try:
                source_path = download_file_from_url(url, upload_folder)
                logger.info(f"OCR file downloaded from URL")
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        
        else:
            return jsonify({'error': 'Provide either "file" or "url"'}), 400
        
        # Validar tamaño
        if source_path.stat().st_size > Config.MAX_FILE_SIZE:
            source_path.unlink()
            logger.warning(f"OCR file too large: {source_path.stat().st_size} bytes")
            return jsonify({'error': f'File too large. Maximum size is {Config.MAX_FILE_SIZE / (1024*1024):.0f}MB'}), 413
        
        # Determinar tipo de archivo
        file_ext = source_path.suffix.lower()
        
        # Procesar según tipo
        if file_ext == '.pdf':
            max_pages = int(os.getenv('OCR_MAX_PAGES', 50))
            result = ocr_processor.extract_text_from_pdf(
                str(source_path),
                lang=lang,
                preprocess=preprocess,
                max_pages=max_pages if max_pages > 0 else None
            )
        else:
            # Asumir que es imagen
            result = ocr_processor.extract_text_from_image(
                str(source_path),
                lang=lang,
                preprocess=preprocess
            )
        
        # Limpiar archivo temporal
        if source_path.exists():
            source_path.unlink()
        
        if result['success']:
            logger.info(f"OCR extraction successful (lang: {lang}, confidence: {result.get('confidence', 0)})")
        else:
            logger.error(f"OCR extraction failed: {result.get('error', 'Unknown error')}")
        
        return jsonify(result), 200 if result['success'] else 500
    
    except Exception as e:
        logger.error(f"OCR error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/ocr/languages', methods=['GET'])
def get_ocr_languages():
    """
    Obtiene la lista de idiomas disponibles para OCR.
    """
    if not ocr_enabled:
        return jsonify({'error': 'OCR functionality is disabled'}), 503
    
    try:
        available_langs = ocr_processor.get_available_languages()
        return jsonify({
            'available': available_langs,
            'supported': OCRProcessor.SUPPORTED_LANGUAGES
        })
    except Exception as e:
        logger.error(f"Error getting OCR languages: {str(e)}")
        return jsonify({'error': str(e)}), 500
