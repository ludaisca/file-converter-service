from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
import requests
from pathlib import Path

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = '/app/uploads'
CONVERTED_FOLDER = '/app/converted'
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50)) * 1024 * 1024  # MB to bytes
MAX_DOWNLOAD_SIZE = int(os.getenv('MAX_DOWNLOAD_SIZE', 100)) * 1024 * 1024  # Para URLs

# Formatos soportados
SUPPORTED_CONVERSIONS = {
    'document': {
        'from': ['.docx', '.doc', '.odt', '.rtf', '.txt'],
        'to': ['.pdf', '.docx', '.txt', '.html']
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
        # Documentos con LibreOffice
        if from_ext in ['.docx', '.doc', '.odt', '.rtf'] and to_ext == '.pdf':
            subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'pdf',
                '--outdir', CONVERTED_FOLDER, input_path
            ], check=True)
            return {'success': True}
        
        # Imágenes con ImageMagick
        elif from_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'] and to_ext in ['.jpg', '.png', '.pdf', '.webp']:
            subprocess.run([
                'convert', input_path, output_path
            ], check=True)
            return {'success': True}
        
        # Video con FFmpeg
        elif from_ext in ['.mp4', '.avi', '.mov', '.mkv'] and to_ext in ['.mp4', '.avi', '.gif']:
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
