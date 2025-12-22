from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
from pathlib import Path

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = '/app/uploads'
CONVERTED_FOLDER = '/app/converted'
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50)) * 1024 * 1024  # MB to bytes

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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'file-converter'})

@app.route('/formats', methods=['GET'])
def get_supported_formats():
    return jsonify(SUPPORTED_CONVERSIONS)

@app.route('/convert', methods=['POST'])
def convert_file():
    try:
        # Validar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        target_format = request.form.get('format', '').lower()
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        if not target_format:
            return jsonify({'error': 'Target format not specified'}), 400
        
        # Generar nombre único
        file_id = str(uuid.uuid4())
        original_ext = Path(file.filename).suffix.lower()
        input_filename = f"{file_id}{original_ext}"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        
        # Guardar archivo
        file.save(input_path)
        
        # Validar tamaño
        if os.path.getsize(input_path) > MAX_FILE_SIZE:
            os.remove(input_path)
            return jsonify({'error': 'File too large'}), 413
        
        # Convertir archivo
        target_ext = f".{target_format}" if not target_format.startswith('.') else target_format
        output_filename = f"{file_id}{target_ext}"
        output_path = os.path.join(CONVERTED_FOLDER, output_filename)
        
        conversion_result = perform_conversion(input_path, output_path, original_ext, target_ext)
        
        if not conversion_result['success']:
            return jsonify({'error': conversion_result['error']}), 500
        
        # Limpiar archivo original
        os.remove(input_path)
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'download_url': f'/download/{file_id}{target_ext}'
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
