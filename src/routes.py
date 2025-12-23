from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from pathlib import Path
import psutil
import time
from datetime import datetime
from typing import Tuple

from src.config_refactored import settings
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
    get_file_size
)
from src.converters.factory import ConverterFactory
from src.validators import FileValidator
from src.ocr import OCRProcessor
from src.utils import download_file_from_url, gzip_response

main_bp = Blueprint('main', __name__)
converter_factory = ConverterFactory()

# Inicializar OCR processor
ocr_processor = OCRProcessor(
    default_lang=settings.OCR_DEFAULT_LANGUAGE
) if settings.ENABLE_OCR else None


@main_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint con información del sistema.
    
    Returns:
        JSON con estado del servicio y métricas del sistema
    """
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
    """
    Get supported conversion formats.
    
    Returns:
        JSON con formatos soportados
    """
    from src.config import Config
    
    logger.info("Requested supported formats")
    return jsonify({
        'success': True,
        'supported_formats': Config.SUPPORTED_CONVERSIONS,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@main_bp.route('/convert', methods=['POST'])
def convert_file() -> Tuple[dict, int]:
    """
    Convert file between formats.
    
    Soporta:
    - Archivo subido directamente
    - Descarga desde URL
    
    Form Parameters:
        - file: Archivo a convertir (multipart/form-data)
        - url: URL del archivo a descargar
        - format: Formato destino (requerido)
    
    Returns:
        JSON con información de conversión o error
    
    Raises:
        UnsupportedFormatException: Formato no soportado
        FileTooLargeException: Archivo muy grande
        URLDownloadException: Error descargando desde URL
        ConversionFailedException: Error en conversión
    """
    try:
        # Obtener y validar formato destino
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

        # 1) Archivo subido
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = sanitize_filename(secure_filename(file.filename))
            
            if not filename or not is_allowed_extension(filename):
                raise InvalidFileException(f"Invalid filename: {filename}")
            
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            source_path = upload_folder / unique_name
            file.save(source_path)
            logger.info(f"File uploaded: {unique_name}")

        # 2) URL remota
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

        # Validar tamaño del archivo
        file_size = get_file_size(source_path)
        max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        
        if source_path.stat().st_size > settings.MAX_FILE_SIZE:
            source_path.unlink()
            raise FileTooLargeException(file_size, max_size_mb)

        # Convertir archivo
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

        # Limpiar archivo original
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
    """
    Download converted file.
    
    Args:
        filename: Nombre del archivo a descargar
    
    Returns:
        Archivo o error JSON
    
    Raises:
        FileNotFoundException: Archivo no encontrado
    """
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
    
    Returns:
        JSON con texto extraído o error
    
    Raises:
        OCRDisabledException: OCR deshabilitado
        FileTooLargeException: Archivo muy grande
        OCRProcessingException: Error en procesamiento OCR
    """
    try:
        if not settings.ENABLE_OCR:
            raise OCRDisabledException()
        
        # Obtener parámetros
        lang = request.form.get('lang', settings.OCR_DEFAULT_LANGUAGE)
        preprocess = request.form.get('preprocess', 'true').lower() == 'true'
        
        upload_folder = settings.UPLOAD_FOLDER
        source_path = None
        
        # Obtener archivo (subido o desde URL)
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
        
        # Validar tamaño
        file_size = get_file_size(source_path)
        max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        
        if source_path.stat().st_size > settings.MAX_FILE_SIZE:
            source_path.unlink()
            raise FileTooLargeException(file_size, max_size_mb)
        
        # Determinar tipo de archivo
        file_ext = source_path.suffix.lower()
        
        # Procesar según tipo
        if file_ext == '.pdf':
            max_pages = settings.OCR_MAX_PAGES
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
    """
    Obtiene la lista de idiomas disponibles para OCR.
    
    Returns:
        JSON con idiomas disponibles
    
    Raises:
        OCRDisabledException: OCR deshabilitado
    """
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
