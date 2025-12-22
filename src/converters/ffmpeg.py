from .base import BaseConverter

class FFmpegConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str, from_ext: str, to_ext: str) -> dict:
        # Video
        if from_ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'] and to_ext in ['.mp4', '.avi', '.gif']:
            return self.run_command([
                'ffmpeg', '-i', input_path, '-y', output_path
            ])
        # Audio
        elif from_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac'] and to_ext in ['.mp3', '.wav', '.ogg']:
            return self.run_command([
                'ffmpeg', '-i', input_path, '-y', output_path
            ])
        return {'success': False, 'error': 'Conversion not supported by FFmpeg'}
