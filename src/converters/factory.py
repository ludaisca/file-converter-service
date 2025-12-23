from .libreoffice import LibreOfficeConverter
from .imagemagick import ImageMagickConverter
from .ffmpeg import FFmpegConverter
from .archive import ArchiveConverter

class ConverterFactory:
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
        # Listas de definición (Deben coincidir con los converters individuales)

        # Archivos Comprimidos
        archive_input = ['.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.xz']
        archive_output = ['.zip', '.7z', '.tar', '.tar.gz', '.gz']
        if from_ext in archive_input and to_ext in archive_output:
            return self.converters['archive']

        # Documentos, Hojas de Cálculo, Presentaciones (LibreOffice)
        doc_input = [
            '.docx', '.doc', '.odt', '.rtf', '.txt', '.html', '.htm',
            '.xlsx', '.xls', '.csv', '.ods',
            '.pptx', '.ppt', '.odp'
        ]
        doc_output = [
            '.pdf', '.docx', '.doc', '.txt', '.html', '.odt', '.rtf',
            '.xlsx', '.xls', '.csv', '.ods',
            '.pptx', '.ppt', '.odp'
        ]
        if from_ext in doc_input and to_ext in doc_output:
            # Prioridad: Si es imagen -> imagen, usar ImageMagick.
            # Pero aquí son documentos.
            return self.converters['libreoffice']

        # Imágenes (ImageMagick)
        img_input = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.svg', '.heic', '.avif', '.ico', '.psd', '.xcf'
        ]
        img_output = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
            '.tiff', '.ico', '.pdf', '.svg'
        ]
        if from_ext in img_input and to_ext in img_output:
            return self.converters['imagemagick']

        # Audio / Video (FFmpeg)
        av_input = [
            '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm',
            '.m4v', '.3gp', '.f4v', '.m2ts', '.mts', '.ts',
            '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac',
            '.opus', '.wma', '.aiff', '.ape'
        ]
        av_output = [
            '.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif', '.webp', '.3gp',
            '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac',
            '.opus', '.wma', '.aiff'
        ]
        if from_ext in av_input and to_ext in av_output:
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
