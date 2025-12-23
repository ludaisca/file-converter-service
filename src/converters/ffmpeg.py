from .base import BaseConverter

class FFmpegConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str, from_ext: str, to_ext: str) -> dict:
        # Listas extendidas de formatos soportados
        video_input = [
            '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm',
            '.m4v', '.3gp', '.f4v', '.m2ts', '.mts', '.ts'
        ]
        video_output = [
            '.mp4', '.avi', '.mov', '.mkv', '.webm', '.gif', '.webp', '.3gp'
        ]

        audio_input = [
            '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac',
            '.opus', '.wma', '.aiff', '.ape'
        ]
        audio_output = [
            '.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac',
            '.opus', '.wma', '.aiff'
        ]

        # Video
        if from_ext in video_input and to_ext in video_output:
            return self.run_command([
                'ffmpeg', '-i', input_path, '-y', output_path
            ])

        # Audio
        elif from_ext in audio_input and to_ext in audio_output:
            return self.run_command([
                'ffmpeg', '-i', input_path, '-y', output_path
            ])

        # Extracción de Audio desde Video (Video -> Audio)
        elif from_ext in video_input and to_ext in audio_output:
             return self.run_command([
                'ffmpeg', '-i', input_path, '-vn', '-y', output_path
            ])

        return {'success': False, 'error': 'Conversion not supported by FFmpeg'}
