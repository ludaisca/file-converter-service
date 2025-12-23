"""
Validación de archivos subidos
"""
import magic
import os
import clamd
from werkzeug.utils import secure_filename
from src.config import settings
from src.exceptions import SecurityException
from src.logging import logger

class FileValidator:
    """Validador de archivos subidos"""
    
    # MIME types permitidos por categoría
    ALLOWED_MIMES = {
        'documents': [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.oasis.opendocument.text',
            'application/rtf',
            'text/plain',
            'text/html',
        ],
        'images': [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/tiff',
            'image/webp',
            'image/svg+xml',
        ],
        'audio': [
            'audio/mpeg',
            'audio/wav',
            'audio/ogg',
            'audio/mp4',
            'audio/x-m4a',
            'audio/flac',
        ],
        'video': [
            'video/mp4',
            'video/x-msvideo',
            'video/quicktime',
            'video/x-matroska',
            'video/x-flv',
            'video/x-ms-wmv',
        ]
    }
    
    @staticmethod
    def validate_file(file, max_size_mb=None):
        """
        Valida un archivo subido
        
        Args:
            file: FileStorage object de Flask
            max_size_mb: Tamaño máximo en MB (None usa settings.MAX_FILE_SIZE)
            
        Returns:
            tuple: (is_valid, error_message, mime_type)
        """
        if max_size_mb is None:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            
        # Verificar que hay un archivo
        if not file or file.filename == '':
            return False, "No file provided", None
            
        # Sanitizar nombre de archivo
        filename = secure_filename(file.filename)
        if not filename:
            return False, "Invalid filename", None
            
        # Verificar extensión
        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            return False, "File must have an extension", None
            
        # Leer primeros bytes para detectar MIME type
        file.seek(0)
        header = file.read(2048)
        file.seek(0)
        
        try:
            mime = magic.from_buffer(header, mime=True)
        except Exception as e:
            return False, f"Could not detect file type: {str(e)}", None
            
        # Verificar que el MIME type está permitido
        allowed = False
        for category_mimes in FileValidator.ALLOWED_MIMES.values():
            if mime in category_mimes:
                allowed = True
                break

        # Allow some flexibility for binary/octet-stream if extension is whitelisted elsewhere,
        # but for now stick to previous strict logic unless we want to break things.
        # Actually, previous logic was strict.
        if not allowed:
            # Fallback for some common types not in list (like docx sometimes showing as zip)
            if mime in ['application/zip', 'application/x-zip-compressed'] and ext in ['.docx', '.xlsx', '.pptx', '.odt', '.ods', '.odp']:
                 allowed = True
            else:
                 return False, f"File type not allowed: {mime}", mime
            
        # Verificar tamaño
        file.seek(0, os.SEEK_END)
        size_bytes = file.tell()
        file.seek(0)
        
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"File too large: {size_mb:.2f}MB (max: {max_size_mb}MB)", mime
            
        return True, None, mime
    
    @staticmethod
    def get_file_category(mime_type):
        """
        Obtiene la categoría de un archivo por su MIME type
        
        Args:
            mime_type: MIME type del archivo
            
        Returns:
            str: Categoría ('documents', 'images', 'audio', 'video') o None
        """
        for category, mimes in FileValidator.ALLOWED_MIMES.items():
            if mime_type in mimes:
                return category
        return None

def scan_file(file_path: str):
    """
    Scans a file using ClamAV.
    Raises SecurityException if the file is infected.
    """
    if not settings.ENABLE_ANTIVIRUS:
        return

    try:
        cd = clamd.ClamdNetworkSocket(settings.CLAMD_HOST, settings.CLAMD_PORT)
        if not cd.ping():
            logger.warning("ClamAV not reachable, skipping scan (soft fail)")
            return

        with open(file_path, 'rb') as f:
            result = cd.instream(f)

        if result and result['stream'][0] == 'FOUND':
            virus_name = result['stream'][1]
            logger.critical(f"Virus found in {file_path}: {virus_name}")
            raise SecurityException(f"File infected with {virus_name}")

        logger.info(f"File {file_path} is clean")

    except SecurityException:
        raise
    except Exception as e:
        logger.error(f"ClamAV scan error: {e}")
        pass
