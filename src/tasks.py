import os
import time
from pathlib import Path
from src.worker import celery_app
from src.converters.factory import ConverterFactory
from src.logging import logger
from src.config import settings
from src.utils import get_file_size
from src.metrics import CONVERSION_DURATION, FILES_PROCESSED, CONVERSION_ERRORS
from src.validators import FileValidator

converter_factory = ConverterFactory()

@celery_app.task(bind=True)
def convert_task(self, source_path_str: str, output_path_str: str, original_ext: str, target_ext: str):
    file_id = Path(source_path_str).stem.split('_')[0]
    logger.info(f"Starting async conversion {original_ext} -> {target_ext} (ID: {file_id})")

    self.update_state(state='PROCESSING', meta={'progress': 0})

    start_time = time.time()

    try:
        # Determine category for metrics
        category = 'unknown'
        for cat, formats in settings.SUPPORTED_CONVERSIONS.items():
            if original_ext in formats['from']:
                category = cat
                break

        conversion_result = converter_factory.perform_conversion(
            source_path_str,
            output_path_str,
            original_ext,
            target_ext
        )

        duration = time.time() - start_time
        CONVERSION_DURATION.labels(source_format=original_ext, target_format=target_ext).observe(duration)

        if not conversion_result['success']:
            raise Exception(conversion_result.get('error', 'Unknown error'))

        output_size = get_file_size(Path(output_path_str))

        FILES_PROCESSED.labels(category=category, status='success').inc()

        # Cleanup source
        source_path = Path(source_path_str)
        if source_path.exists():
            source_path.unlink()

        return {
            'success': True,
            'file_id': file_id,
            'output_filename': Path(output_path_str).name,
            'output_size_mb': output_size,
            'download_url': f'/download/{Path(output_path_str).name}'
        }

    except Exception as e:
        duration = time.time() - start_time
        # Record failure metric
        exc_type = type(e).__name__
        CONVERSION_ERRORS.labels(exception_type=exc_type).inc()
        FILES_PROCESSED.labels(category='unknown', status='error').inc()

        logger.error(f"Async conversion failed: {e}")
        # Cleanup source on failure too
        if os.path.exists(source_path_str):
            os.remove(source_path_str)

        # Custom state for error
        self.update_state(
            state='FAILURE',
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),
            }
        )
        raise e
