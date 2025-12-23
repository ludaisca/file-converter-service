from .libreoffice import LibreOfficeConverter
from .imagemagick import ImageMagickConverter
from .ffmpeg import FFmpegConverter

class ConverterFactory:
    def __init__(self):
        self.converters = {
            'libreoffice': LibreOfficeConverter(),
            'imagemagick': ImageMagickConverter(),
            'ffmpeg': FFmpegConverter()
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
        # Documentos - LibreOffice
        if from_ext in ['.docx', '.doc', '.odt', '.rtf', '.txt'] and to_ext in ['.pdf', '.docx', '.txt', '.html']:
            return self.converters['libreoffice']

        # Imágenes - ImageMagick
        if from_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'] and to_ext in ['.jpg', '.png', '.pdf', '.webp']:
            return self.converters['imagemagick']

        # Video - FFmpeg
        if from_ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'] and to_ext in ['.mp4', '.avi', '.gif']:
            return self.converters['ffmpeg']

        # Audio - FFmpeg
        if from_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac'] and to_ext in ['.mp3', '.wav', '.ogg']:
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
