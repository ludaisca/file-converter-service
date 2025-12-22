from .base import BaseConverter

class ImageMagickConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str, from_ext: str, to_ext: str) -> dict:
        if from_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'] and to_ext in ['.jpg', '.png', '.pdf', '.webp']:
            return self.run_command([
                'convert', input_path, output_path
            ])
        return {'success': False, 'error': 'Conversion not supported by ImageMagick'}
