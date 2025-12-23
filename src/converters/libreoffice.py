from .base import BaseConverter
from ..config import Config
import os
import shutil

class LibreOfficeConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str, from_ext: str, to_ext: str) -> dict:
        """
        Convierte documentos usando LibreOffice
        Soporta: DOCX, DOC, ODT, RTF, TXT -> PDF, DOCX, TXT, HTML
        """
        # Formatos soportados por LibreOffice
        supported_input = ['.docx', '.doc', '.odt', '.rtf', '.txt']
        supported_output = ['.pdf', '.docx', '.txt', '.html']
        
        if from_ext not in supported_input:
            return {'success': False, 'error': f'Input format {from_ext} not supported by LibreOffice'}
        
        if to_ext not in supported_output:
            return {'success': False, 'error': f'Output format {to_ext} not supported by LibreOffice'}
        
        # Determinar formato de salida para LibreOffice
        format_map = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.txt': 'txt',
            '.html': 'html'
        }
        
        output_format = format_map.get(to_ext)
        if not output_format:
            return {'success': False, 'error': f'Unknown output format: {to_ext}'}
        
        # LibreOffice genera el archivo en --outdir con el mismo nombre base
        # Ejecutar conversión
        result = self.run_command([
            'libreoffice',
            '--headless',
            '--convert-to', output_format,
            '--outdir', Config.CONVERTED_FOLDER,
            input_path
        ])
        
        if not result['success']:
            return result
        
        # LibreOffice crea el archivo con el nombre base del input + nueva extensión
        # Necesitamos renombrarlo si es necesario
        input_basename = os.path.basename(input_path)
        input_name_without_ext = os.path.splitext(input_basename)[0]
        expected_output = os.path.join(Config.CONVERTED_FOLDER, f"{input_name_without_ext}{to_ext}")
        
        # Si el archivo esperado existe pero no es el output_path, renombrar
        if os.path.exists(expected_output) and expected_output != output_path:
            shutil.move(expected_output, output_path)
        
        # Verificar que el archivo de salida existe
        if os.path.exists(output_path):
            return {'success': True}
        elif os.path.exists(expected_output):
            return {'success': True}
        else:
            return {'success': False, 'error': 'Output file not created by LibreOffice'}
