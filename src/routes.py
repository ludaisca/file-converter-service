from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from pathlib import Path
import psutil
import time
from datetime import datetime
from typing import Tuple

from src.config import settings
from src.logging import logger
from src.exceptions import (
    FileConverterException,
    InvalidFileException,
    UnsupportedFormatException,
    ConversionFailedException,
    FileTooLargeException,
    FileNotFoundException,
    OCRDisabledException,
    OCRProcessingException,
    URLDownloadException
)
from src.utils import (
    get_allowed_extensions,
    is_allowed_extension,
    get_file_extension,
    sanitize_filename,
    get_file_size,
    download_file_from_url,
    gzip_response
)
from src.converters.factory import ConverterFactory
from src.validators import FileValidator
from src.ocr import OCRProcessor

main_bp = Blueprint('main', __name__)
converter_factory = ConverterFactory()

ocr_processor = OCRProcessor(
    default_lang=settings.OCR_DEFAULT_LANGUAGE
) if settings.ENABLE_OCR else None

def register_routes(app):
    app.register_blueprint(main_bp)

@main_bp.route('/health', methods=['GET'])
def health_check():
    try:
        disk_usage = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()

        health_data = {
            'success': True,
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
                'version': '2.0.0',
                'upload_folder_exists': settings.UPLOAD_FOLDER.exists(),
                'converted_folder_exists': settings.CONVERTED_FOLDER.exists(),
                'logs_folder_exists': settings.LOGS_FOLDER.exists()
            },
            'features': {
                'ocr_enabled': settings.ENABLE_OCR,
                'ocr_languages': ocr_processor.get_available_languages() if ocr_processor else []
            }
        }

        logger.info("Health check performed successfully")
        return jsonify(health_data), 200

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': 'Health check failed',
            'error_code': 'HEALTH_CHECK_FAILED',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@main_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    from src.config import Config
    logger.info("Requested supported formats")
    return jsonify({
        'success': True,
        'supported_formats': Config.SUPPORTED_CONVERSIONS,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@main_bp.route('/convert', methods=['POST'])
def convert_file() -> Tuple[dict, int]:
    try:
        target_format = request.form.get('format', '').lower().strip()
        
        if not target_format:
            raise UnsupportedFormatException(
                '',
                supported_formats=get_allowed_extensions()
            )
        
        if not is_allowed_extension(f"file.{target_format}"):
            raise UnsupportedFormatException(
                target_format,
                supported_formats=get_allowed_extensions()
            )
        
        upload_folder = settings.UPLOAD_FOLDER
        source_path = None

        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = sanitize_filename(secure_filename(file.filename))
            
            if not filename or not is_allowed_extension(filename):
                raise InvalidFileException(f"Invalid filename: {filename}")
            
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            source_path = upload_folder / unique_name
            file.save(source_path)
            logger.info(f"File uploaded: {unique_name}")

        elif 'url' in request.form:
            url = request.form.get('url', '').strip()
            if not url:
                raise URLDownloadException('', 'Empty URL provided')
            
            try:
                source_path = download_file_from_url(url, upload_folder)
                logger.info(f"File downloaded from URL: {url}")
            except ValueError as e:
                raise URLDownloadException(url, str(e))

        else:
            raise InvalidFileException(
                'Provide either "file" (multipart) or "url" parameter',
                details={'expected': ['file', 'url']}
            )

        file_size = get_file_size(source_path)
        max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        
        if source_path.stat().st_size > settings.MAX_FILE_SIZE:
            source_path.unlink()
            raise FileTooLargeException(file_size, max_size_mb)

        original_ext = source_path.suffix.lower()
        target_ext = f".{target_format}" if not target_format.startswith('.') else target_format
        file_id = source_path.stem.split('_')[0]
        output_filename = f"{file_id}{target_ext}"
        output_path = settings.CONVERTED_FOLDER / output_filename

        logger.info(f"Starting conversion {original_ext} → {target_ext} (ID: {file_id})")

        conversion_result = converter_factory.perform_conversion(
            str(source_path),
            str(output_path),
            original_ext,
            target_ext
        )

        if not conversion_result['success']:
            if source_path.exists():
                source_path.unlink()
            raise ConversionFailedException(
                conversion_result.get('error', 'Unknown error'),
                source_format=original_ext,
                target_format=target_ext
            )

        if source_path.exists():
            source_path.unlink()

        logger.info(f"Conversion completed successfully (ID: {file_id})")

        return jsonify({
            'success': True,
            'file_id': file_id,
            'source_format': original_ext,
            'output_format': target_format,
            'output_size_mb': get_file_size(output_path),
            'download_url': f'/download/{output_filename}',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except FileConverterException as e:
        logger.warning(f"{e.error_code}: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Unexpected conversion error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Conversion failed',
            'error_code': 'CONVERSION_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@main_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename: str):
    try:
        safe_filename = secure_filename(filename)
        file_path = settings.CONVERTED_FOLDER / safe_filename
        
        if not file_path.exists():
            raise FileNotFoundException(safe_filename)
        
        logger.info(f"File downloaded: {safe_filename}")
        return send_file(file_path, as_attachment=True)
    
    except FileConverterException as e:
        logger.warning(f"{e.error_code}: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Download failed',
            'error_code': 'DOWNLOAD_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@main_bp.route('/extract-text', methods=['POST'])
def extract_text():
    try:
        if not settings.ENABLE_OCR:
            raise OCRDisabledException()
        
        lang = request.form.get('lang', settings.OCR_DEFAULT_LANGUAGE)
        preprocess = request.form.get('preprocess', 'true').lower() == 'true'
        
        upload_folder = settings.UPLOAD_FOLDER
        source_path = None
        
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = sanitize_filename(secure_filename(file.filename))
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            source_path = upload_folder / unique_name
            file.save(source_path)
            logger.info(f"OCR file uploaded: {unique_name}")
        
        elif 'url' in request.form:
            url = request.form.get('url', '').strip()
            if not url:
                raise URLDownloadException('', 'Empty URL provided')
            
            try:
                source_path = download_file_from_url(url, upload_folder)
                logger.info(f"OCR file downloaded from URL")
            except ValueError as e:
                raise URLDownloadException(url, str(e))
        
        else:
            raise InvalidFileException(
                'Provide either "file" or "url" parameter'
            )
        
        file_size = get_file_size(source_path)
        max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        
        if source_path.stat().st_size > settings.MAX_FILE_SIZE:
            source_path.unlink()
            raise FileTooLargeException(file_size, max_size_mb)
        
        file_ext = source_path.suffix.lower()
        
        if file_ext == '.pdf':
            max_pages = settings.OCR_MAX_PAGES
            result = ocr_processor.extract_text_from_pdf(
                str(source_path),
                lang=lang,
                preprocess=preprocess,
                max_pages=max_pages if max_pages > 0 else None
            )
        else:
            result = ocr_processor.extract_text_from_image(
                str(source_path),
                lang=lang,
                preprocess=preprocess
            )
        
        if source_path.exists():
            source_path.unlink()
        
        if result['success']:
            logger.info(f"OCR extraction successful (lang: {lang}, confidence: {result.get('confidence', 0)})")
            return jsonify({
                'success': True,
                'text': result.get('text', ''),
                'confidence': result.get('confidence', 0),
                'language': lang,
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        else:
            raise OCRProcessingException(
                result.get('error', 'Unknown OCR error'),
                language=lang
            )
    
    except FileConverterException as e:
        logger.warning(f"{e.error_code}: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"OCR error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'OCR processing failed',
            'error_code': 'OCR_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@main_bp.route('/ocr/languages', methods=['GET'])
def get_ocr_languages():
    try:
        if not settings.ENABLE_OCR:
            raise OCRDisabledException()
        
        available_langs = ocr_processor.get_available_languages()
        return jsonify({
            'success': True,
            'available': available_langs,
            'supported': OCRProcessor.SUPPORTED_LANGUAGES,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except FileConverterException as e:
        logger.warning(f"{e.error_code}: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Error getting OCR languages: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to get OCR languages',
            'error_code': 'OCR_LANGUAGES_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
