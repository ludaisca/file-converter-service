from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
import requests
from pathlib import Path
import threading
import time

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = '/app/uploads'
CONVERTED_FOLDER = '/app/converted'
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50)) * 1024 * 1024  # MB to bytes
MAX_DOWNLOAD_SIZE = int(os.getenv('MAX_DOWNLOAD_SIZE', 100)) * 1024 * 1024  # Para URLs
CLEANUP_INTERVAL = 3600  # 1 hour
FILE_TTL = 3600         # 1 hour

# Formatos soportados
SUPPORTED_CONVERSIONS = {
    'document': {
        'from': ['.docx', '.doc', '.odt', '.rtf', '.txt', '.md', '.html'],
        'to': ['.pdf', '.docx', '.txt', '.html', '.odt', '.md']
    },
    'image': {
        'from': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
        'to': ['.jpg', '.png', '.pdf', '.webp']
    },
    'video': {
        'from': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'],
        'to': ['.mp4', '.avi', '.gif']
    },
    'audio': {
        'from': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
        'to': ['.mp3', '.wav', '.ogg']
    }
}

def cleanup_files():
    """Background task to clean up old files."""
    while True:
        try:
            now = time.time()
            for folder in [UPLOAD_FOLDER, CONVERTED_FOLDER]:
                if not os.path.exists(folder):
                    continue
                for f in os.listdir(folder):
                    f_path = os.path.join(folder, f)
                    try:
                        if os.path.isfile(f_path):
                            if os.stat(f_path).st_mtime < now - FILE_TTL:
                                os.remove(f_path)
                    except Exception as e:
                        print(f"Error processing {f_path}: {e}")
        except Exception as e:
            print(f"Error in cleanup loop: {e}")
        time.sleep(CLEANUP_INTERVAL)

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_files, daemon=True)
cleanup_thread.start()

def download_file_from_url(url: str, upload_folder: Path) -> Path:
    """Descarga un archivo desde una URL remota"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Obtener nombre original de la URL
        original_name = url.split('/')[-1] or 'downloaded_file'
        name, ext = os.path.splitext(original_name)
        
        # Generar nombre único y seguro
        safe_name = secure_filename(name) or 'file'
        unique_name = f"{uuid.uuid4().hex}_{safe_name}{ext}"
        file_path = upload_folder / unique_name
        
        # Descargar archivo con validación de tamaño
        size = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    size += len(chunk)
                    if size > MAX_DOWNLOAD_SIZE:
                        file_path.unlink()
                        raise ValueError(f'Downloaded file exceeds maximum size of {MAX_DOWNLOAD_SIZE / (1024*1024):.0f}MB')
                    f.write(chunk)
        
        return file_path
    except requests.exceptions.RequestException as e:
        raise ValueError(f'Error downloading file from URL: {str(e)}')
    except Exception as e:
        raise ValueError(f'Error processing downloaded file: {str(e)}')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'file-converter'})

@app.route('/formats', methods=['GET'])
def get_supported_formats():
    return jsonify(SUPPORTED_CONVERSIONS)

@app.route('/convert', methods=['POST'])
def convert_file():
    try:
        target_format = request.form.get('format', '').lower()
        
        if not target_format:
            return jsonify({'error': 'Target format not specified'}), 400
        
        upload_folder = Path(UPLOAD_FOLDER)
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        source_path = None
        
        # 1) Archivo subido
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            filename = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{filename}"
            source_path = upload_folder / unique_name
            file.save(source_path)
        
        # 2) URL remota
        elif 'url' in request.form:
            url = request.form.get('url', '').strip()
            if not url:
                return jsonify({'error': 'Empty URL provided'}), 400
            try:
                source_path = download_file_from_url(url, upload_folder)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        
        else:
            return jsonify({'error': 'Provide either "file" or "url"'}), 400
        
        # Validar tamaño del archivo
        if source_path.stat().st_size > MAX_FILE_SIZE:
            source_path.unlink()
            return jsonify({'error': f'File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB'}), 413
        
        # Convertir archivo
        original_ext = source_path.suffix.lower()
        target_ext = f".{target_format}" if not target_format.startswith('.') else target_format
        file_id = source_path.stem.split('_')[0]
        output_filename = f"{file_id}{target_ext}"
        output_path = Path(CONVERTED_FOLDER) / output_filename
        
        conversion_result = perform_conversion(str(source_path), str(output_path), original_ext, target_ext)
        
        if not conversion_result['success']:
            if source_path.exists():
                source_path.unlink()
            return jsonify({'error': conversion_result['error']}), 500
        
        # Limpiar archivo original
        if source_path.exists():
            source_path.unlink()
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'output_format': target_format,
            'download_url': f'/download/{output_filename}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(CONVERTED_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_conversion(input_path, output_path, from_ext, to_ext):
    try:
        # LibreOffice conversions
        libreoffice_formats = ['.docx', '.doc', '.odt', '.rtf', '.txt', '.html']
        libreoffice_targets = ['.pdf', '.docx', '.txt', '.html', '.odt']

        if from_ext in libreoffice_formats and to_ext in libreoffice_targets:
            # Construct expected LibreOffice output filename
            # LibreOffice uses the input filename stem + new extension
            input_stem = Path(input_path).stem
            temp_output_filename = f"{input_stem}{to_ext}"
            temp_output_path = Path(CONVERTED_FOLDER) / temp_output_filename

            format_arg = to_ext.lstrip('.')
            # Special case for text
            if format_arg == 'txt':
                format_arg = 'txt:Text'

            cmd = ['libreoffice', '--headless', '--convert-to', format_arg, '--outdir', CONVERTED_FOLDER, input_path]
            subprocess.run(cmd, check=True)

            # Check if file exists and rename
            if temp_output_path.exists():
                if temp_output_path != Path(output_path):
                    if Path(output_path).exists():
                        Path(output_path).unlink()
                    temp_output_path.rename(output_path)
                return {'success': True}
            else:
                 # If temp file not found, check if maybe it was saved with different extension?
                 # E.g. .html might save as .html, but sometimes .htm?
                 # For now assume it failed.
                 return {'success': False, 'error': 'LibreOffice conversion failed to produce output file'}
        
        # Pandoc conversions (MarkDown, etc)
        elif from_ext == '.md' or to_ext == '.md':
             cmd = ['pandoc', input_path, '-o', output_path]
             subprocess.run(cmd, check=True)
             return {'success': True}

        # Imágenes con ImageMagick
        elif from_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'] and to_ext in ['.jpg', '.png', '.pdf', '.webp']:
            subprocess.run([
                'convert', input_path, output_path
            ], check=True)
            return {'success': True}
        
        # Video con FFmpeg
        elif from_ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'] and to_ext in ['.mp4', '.avi', '.gif']:
            subprocess.run([
                'ffmpeg', '-i', input_path, '-y', output_path
            ], check=True)
            return {'success': True}
        
        # Audio con FFmpeg
        elif from_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac'] and to_ext in ['.mp3', '.wav', '.ogg']:
            subprocess.run([
                'ffmpeg', '-i', input_path, '-y', output_path
            ], check=True)
            return {'success': True}
        
        else:
            return {'success': False, 'error': 'Conversion not supported'}
        
    except subprocess.CalledProcessError as e:
        return {'success': False, 'error': f'Conversion failed: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CONVERTED_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
