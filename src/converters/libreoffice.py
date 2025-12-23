from .base import BaseConverter
from ..config import Config
import os
import shutil

class LibreOfficeConverter(BaseConverter):
    def convert(self, input_path: str, output_path: str, from_ext: str, to_ext: str) -> dict:
        """
        Convierte documentos, hojas de cálculo y presentaciones usando LibreOffice.
        Soporta una amplia gama de formatos de Office y Texto.
        """
        # Formatos soportados
        supported_input = [
            # Documentos
            '.docx', '.doc', '.odt', '.rtf', '.txt', '.pdf', '.html', '.htm',
            # Hojas de cálculo
            '.xlsx', '.xls', '.csv', '.ods',
            # Presentaciones
            '.pptx', '.ppt', '.odp'
        ]

        supported_output = [
            # Documentos
            '.pdf', '.docx', '.doc', '.txt', '.html', '.odt', '.rtf',
            # Hojas de cálculo
            '.xlsx', '.xls', '.csv', '.ods',
            # Presentaciones
            '.pptx', '.ppt', '.odp'
        ]
        
        if from_ext not in supported_input:
            return {'success': False, 'error': f'Input format {from_ext} not supported by LibreOffice'}
        
        if to_ext not in supported_output:
            return {'success': False, 'error': f'Output format {to_ext} not supported by LibreOffice'}
        
        # Mapeo de extensiones a filtros de conversión de LibreOffice (si es necesario ser explícito)
        # En general, pasar la extensión destino funciona, pero algunos casos requieren cuidado.
        format_map = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.doc': 'doc',
            '.txt': 'txt',
            '.html': 'html',
            '.odt': 'odt',
            '.rtf': 'rtf',
            '.xlsx': 'xlsx',
            '.xls': 'xls',
            '.csv': 'csv',
            '.ods': 'ods',
            '.pptx': 'pptx',
            '.ppt': 'ppt',
            '.odp': 'odp'
        }
        
        output_format = format_map.get(to_ext)
        if not output_format:
            return {'success': False, 'error': f'Unknown output format: {to_ext}'}

        # Ejecutar conversión
        # --convert-to identifica el filtro de salida basado en la extensión proporcionada
        result = self.run_command([
            'libreoffice',
            '--headless',
            '--convert-to', output_format,
            '--outdir', Config.CONVERTED_FOLDER,
            input_path
        ])
        
        if not result['success']:
            return result
        
        # Lógica de renombrado
        input_basename = os.path.basename(input_path)
        input_name_without_ext = os.path.splitext(input_basename)[0]

        # LibreOffice a veces cambia la extensión ligeramente (ej: .htm -> .html)
        # Intentamos predecir el nombre de salida
        expected_output = os.path.join(Config.CONVERTED_FOLDER, f"{input_name_without_ext}{to_ext}")
        
        # Si la extensión de salida es .html, LibreOffice puede generar varios archivos
        # o usar una extensión diferente.

        if os.path.exists(expected_output) and expected_output != output_path:
            shutil.move(expected_output, output_path)

        # Verificar existencia
        if os.path.exists(output_path):
            return {'success': True}

        # Búsqueda fallback si el nombre no es exacto
        # (Por ejemplo si convertimos a .csv y LibreOffice usa otra convención o si input tenía multiples puntos)

        # Listar archivos en converted folder para ver si hay alguno nuevo con el nombre base correcto
        # Esto es arriesgado en concurrencia sin directorios únicos por request,
        # pero mantenemos la lógica actual mejorada.

        return {'success': False, 'error': 'Output file not created by LibreOffice'}
