from .libreoffice import LibreOfficeConverter
from .imagemagick import ImageMagickConverter
from .ffmpeg import FFmpegConverter

class ConverterFactory:
    def __init__(self):
        self.converters = [
            LibreOfficeConverter(),
            ImageMagickConverter(),
            FFmpegConverter()
        ]

    def get_converter(self, from_ext, to_ext):
        # Determine which converter to use based on extensions
        # This logic mimics the if/elif blocks in original perform_conversion

        if from_ext in ['.docx', '.doc', '.odt', '.rtf'] and to_ext == '.pdf':
            return self.converters[0] # LibreOffice

        if from_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'] and to_ext in ['.jpg', '.png', '.pdf', '.webp']:
             return self.converters[1] # ImageMagick

        if from_ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'] and to_ext in ['.mp4', '.avi', '.gif']:
            return self.converters[2] # FFmpeg Video

        if from_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac'] and to_ext in ['.mp3', '.wav', '.ogg']:
            return self.converters[2] # FFmpeg Audio

        return None

    def perform_conversion(self, input_path, output_path, from_ext, to_ext):
        converter = self.get_converter(from_ext, to_ext)
        if converter:
            return converter.convert(input_path, output_path, from_ext, to_ext)
        return {'success': False, 'error': 'Conversion not supported'}
