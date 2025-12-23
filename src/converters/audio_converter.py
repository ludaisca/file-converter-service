"""
Audio Converter Module

Soporta conversión de:
- MP3, WAV, OGG, M4A, FLAC, AAC, OPUS, WMA

Utiliza ffmpeg como backend.
"""

import subprocess
import os
from pathlib import Path
from ..exceptions import ConversionFailedException


class AudioConverter:
    """Convertidor de archivos de audio usando ffmpeg."""

    # Formatos soportados como entrada
    SUPPORTED_INPUT_FORMATS = {
        'mp3': 'MPEG Audio',
        'wav': 'WAV Audio',
        'ogg': 'OGG Vorbis',
        'm4a': 'MPEG-4 Audio',
        'flac': 'FLAC Audio',
        'aac': 'AAC Audio',
        'opus': 'Opus Audio',
        'wma': 'Windows Media Audio',
        'aiff': 'AIFF Audio',
        'ape': 'Monkey\'s Audio',
    }

    # Formatos soportados como salida
    SUPPORTED_OUTPUT_FORMATS = {
        'mp3': {'codec': 'libmp3lame', 'extension': 'mp3', 'bitrate': '192k'},
        'wav': {'codec': 'pcm_s16le', 'extension': 'wav', 'bitrate': ''},
        'ogg': {'codec': 'libvorbis', 'extension': 'ogg', 'bitrate': '192k'},
        'm4a': {'codec': 'aac', 'extension': 'm4a', 'bitrate': '192k'},
        'flac': {'codec': 'flac', 'extension': 'flac', 'bitrate': ''},
        'aac': {'codec': 'aac', 'extension': 'aac', 'bitrate': '192k'},
        'opus': {'codec': 'libopus', 'extension': 'opus', 'bitrate': '192k'},
        'wma': {'codec': 'wmav2', 'extension': 'wma', 'bitrate': '192k'},
        'aiff': {'codec': 'pcm_s16be', 'extension': 'aiff', 'bitrate': ''},
    }

    @staticmethod
    def convert(input_path: str, output_format: str) -> str:
        """
        Convertir archivo de audio a formato especificado.

        Args:
            input_path: Ruta al archivo de audio de entrada
            output_format: Formato de salida (mp3, wav, ogg, m4a, flac, aac, opus, wma)

        Returns:
            Ruta al archivo convertido

        Raises:
            ConversionFailedException: Si la conversión falla
        """
        output_format = output_format.lower()

        if output_format not in AudioConverter.SUPPORTED_OUTPUT_FORMATS:
            raise ConversionFailedException(
                f"Formato de salida no soportado: {output_format}",
                error_code="UNSUPPORTED_AUDIO_FORMAT",
            )

        if not os.path.exists(input_path):
            raise ConversionFailedException(
                f"Archivo de entrada no encontrado: {input_path}",
                error_code="INPUT_FILE_NOT_FOUND",
            )

        # Construir ruta de salida
        input_name = Path(input_path).stem
        output_dir = Path(input_path).parent
        output_extension = AudioConverter.SUPPORTED_OUTPUT_FORMATS[output_format][
            "extension"
        ]
        output_path = output_dir / f"{input_name}.{output_extension}"

        try:
            # Construir comando ffmpeg
            format_config = AudioConverter.SUPPORTED_OUTPUT_FORMATS[output_format]
            codec = format_config["codec"]
            bitrate = format_config.get("bitrate", "")

            cmd = [
                "ffmpeg",
                "-i",
                input_path,
                "-c:a",
                codec,
            ]

            # Agregar bitrate si está configurado
            if bitrate:
                cmd.extend(["-b:a", bitrate])

            # Agregar opciones específicas por formato
            if output_format == "wav":
                cmd.extend(["-acodec", "pcm_s16le"])
            elif output_format == "flac":
                cmd.extend(["-compression_level", "8"])
            elif output_format in ["mp3", "ogg", "aac", "opus"]:
                cmd.extend(["-q:a", "4"])  # Quality level

            # Agregar salida
            cmd.extend(["-y", str(output_path)])

            # Ejecutar conversión
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos de timeout
            )

            if result.returncode != 0:
                raise ConversionFailedException(
                    f"Error en conversión de audio: {result.stderr}",
                    error_code="AUDIO_CONVERSION_ERROR",
                )

            if not output_path.exists():
                raise ConversionFailedException(
                    "Archivo de salida no generado",
                    error_code="OUTPUT_FILE_NOT_CREATED",
                )

            return str(output_path)

        except subprocess.TimeoutExpired:
            raise ConversionFailedException(
                "Conversión de audio excedió el tiempo límite",
                error_code="CONVERSION_TIMEOUT",
            )
        except Exception as e:
            raise ConversionFailedException(
                f"Error inesperado en conversión de audio: {str(e)}",
                error_code="AUDIO_CONVERSION_ERROR",
            )

    @staticmethod
    def get_supported_formats() -> dict:
        """Retornar formatos soportados."""
        return {
            "input": list(AudioConverter.SUPPORTED_INPUT_FORMATS.keys()),
            "output": list(AudioConverter.SUPPORTED_OUTPUT_FORMATS.keys()),
        }
