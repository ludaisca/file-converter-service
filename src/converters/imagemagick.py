from .base import BaseConverter

class ImageMagickConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str, from_ext: str, to_ext: str) -> dict:
        supported_input = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.svg', '.heic', '.avif', '.ico', '.psd', '.xcf'
        ]
        supported_output = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
            '.tiff', '.ico', '.pdf', '.svg'
        ]

        if from_ext in supported_input and to_ext in supported_output:
            return self.run_command([
                'convert', input_path, output_path
            ])
        return {'success': False, 'error': 'Conversion not supported by ImageMagick'}
