import os
import shutil
import tempfile
from .base import BaseConverter
from ..logging import logger

class ArchiveConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str, from_ext: str, to_ext: str) -> dict:
        """
        Convierte archivos comprimidos extrayendo y re-comprimiendo.
        Soporta: ZIP, 7Z, RAR, TAR, GZ, BZ2 -> ZIP, 7Z, TAR, TAR.GZ
        """
        # Formatos soportados
        supported_input = ['.zip', '.7z', '.rar', '.tar', '.gz', '.bz2', '.xz']
        supported_output = ['.zip', '.7z', '.tar', '.tar.gz', '.gz']

        if from_ext not in supported_input:
            return {'success': False, 'error': f'Input format {from_ext} not supported by ArchiveConverter'}

        if to_ext not in supported_output:
            return {'success': False, 'error': f'Output format {to_ext} not supported by ArchiveConverter'}

        # Crear directorio temporal para extracción
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Extraer archivo
            extract_success = self._extract(input_path, temp_dir, from_ext)
            if not extract_success:
                return {'success': False, 'error': 'Failed to extract input archive'}

            # 2. Comprimir al nuevo formato
            compress_success = self._compress(temp_dir, output_path, to_ext)
            if not compress_success:
                return {'success': False, 'error': 'Failed to create output archive'}

        return {'success': True}

    def _extract(self, input_path: str, temp_dir: str, ext: str) -> bool:
        """Extrae el archivo al directorio temporal."""
        try:
            # Usar 7z para la mayoría de extracciones ya que maneja zip, rar, 7z, tar, gz, etc.
            # 'x': eXtract with full paths
            # '-y': assume Yes on all queries
            # '-o': output directory
            cmd = ['7z', 'x', input_path, f'-o{temp_dir}', '-y']
            result = self.run_command(cmd)
            return result['success']
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}")
            return False

    def _compress(self, source_dir: str, output_path: str, ext: str) -> bool:
        """Comprime el contenido del directorio al archivo destino."""
        try:
            # Determinar comando según extensión de salida
            if ext == '.zip':
                # 'a': add
                # '-r': recurse subdirectories (zip handles this by default usually but good to be explicit or pass wildcards)
                # 7z a -tzip output.zip source/*
                cmd = ['7z', 'a', '-tzip', output_path, os.path.join(source_dir, '*')]

            elif ext == '.7z':
                cmd = ['7z', 'a', '-t7z', output_path, os.path.join(source_dir, '*')]

            elif ext == '.tar':
                # tar -cf output.tar -C source_dir .
                cmd = ['tar', '-cf', output_path, '-C', source_dir, '.']

            elif ext == '.tar.gz' or (ext == '.gz' and output_path.endswith('.tar.gz')):
                # tar -czf output.tar.gz -C source_dir .
                cmd = ['tar', '-czf', output_path, '-C', source_dir, '.']

            else:
                return False

            result = self.run_command(cmd)
            return result['success']
        except Exception as e:
            logger.error(f"Compression error: {str(e)}")
            return False
