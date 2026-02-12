from .libreoffice import LibreOfficeConverter
from .imagemagick import ImageMagickConverter
from .ffmpeg import FFmpegConverter
from .archive import ArchiveConverter

class ConverterFactory:
    # Archivos Comprimidos
    ARCHIVE_INPUT = {'.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.xz'}
    ARCHIVE_OUTPUT = {'.zip', '.7z', '.tar', '.tar.gz', '.gz'}

    # Documentos, Hojas de Cálculo, Presentaciones (LibreOffice)
    DOC_INPUT = {
        '.docx', '.doc', '.odt', '.rtf', '.txt', '.html', '.htm',
        '.xlsx', '.xls', '.csv', '.ods',
        '.pptx', '.ppt', '.odp'
    }
    DOC_OUTPUT = {
        '.pdf', '.docx', '.doc', '.txt', '.html', '.odt', '.rtf',
        '.xlsx', '.xls', '.csv', '.ods',
        '.pptx', '.ppt', '.odp'
    }

    # Imágenes (ImageMagick)
    IMG_INPUT = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
        '.webp', '.svg', '.heic', '.avif', '.ico', '.psd', '.xcf'
    }
    IMG_OUTPUT = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
        '.tiff', '.ico', '.pdf', '.svg'
    }

    # Audio / Video (FFmpeg)
    AV_INPUT = {
        '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm',
        '.m4v', '.3gp', '.f4v', '.m2ts', '.mts', '.ts',
        '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac',
        '.opus', '.wma', '.aiff', '.ape'
    }
    AV_OUTPUT = {
        '.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif', '.webp', '.3gp',
        '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac',
        '.opus', '.wma', '.aiff'
    }

    def __init__(self):
        self.converters = {
            'libreoffice': LibreOfficeConverter(),
            'imagemagick': ImageMagickConverter(),
            'ffmpeg': FFmpegConverter(),
            'archive': ArchiveConverter()
        }

    def get_converter(self, from_ext, to_ext):
        """
        Determina qué conversor usar basado en las extensiones
        
        Args:
            from_ext: Extensión de origen (ej: '.txt')
            to_ext: Extensión de destino (ej: '.pdf')
            
        Returns:
            Conversor apropiado o None
        """

        # Archivos Comprimidos
        if from_ext in self.ARCHIVE_INPUT and to_ext in self.ARCHIVE_OUTPUT:
            return self.converters['archive']

        # Documentos, Hojas de Cálculo, Presentaciones (LibreOffice)
        if from_ext in self.DOC_INPUT and to_ext in self.DOC_OUTPUT:
            # Prioridad: Si es imagen -> imagen, usar ImageMagick.
            # Pero aquí son documentos.
            return self.converters['libreoffice']

        # Imágenes (ImageMagick)
        if from_ext in self.IMG_INPUT and to_ext in self.IMG_OUTPUT:
            return self.converters['imagemagick']

        # Audio / Video (FFmpeg)
        if from_ext in self.AV_INPUT and to_ext in self.AV_OUTPUT:
            return self.converters['ffmpeg']

        return None

    def perform_conversion(self, input_path, output_path, from_ext, to_ext):
        """
        Realiza la conversión de archivo
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            from_ext: Extensión de origen
            to_ext: Extensión de destino
            
        Returns:
            dict: Resultado de la conversión
        """
        converter = self.get_converter(from_ext, to_ext)
        if converter:
            return converter.convert(input_path, output_path, from_ext, to_ext)
        return {'success': False, 'error': 'Conversion not supported'}
