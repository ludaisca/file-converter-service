# 🚀 Guía de Migración - FASE 1

## Descripción General

Esta guía te ayuda a migrar el código existente del servicio a la **Fase 1 refactorizada** con excepciones personalizadas, configuración validada con Pydantic, y respuestas JSON estandarizadas.

---

## 1️⃣ Instalación de Dependencias

### Paso 1: Actualizar requirements.txt

```bash
# Ya está actualizado en la rama refactor/phase-1
pip install -r requirements.txt
```

### Dependencias Nuevas Necesarias

```bash
# Pydantic para validación
pip install pydantic>=2.0.0 pydantic-settings>=2.0.0

# Opcionales pero recomendados
pip install mypy>=1.7.1          # Type checking
pip install pytest-asyncio>=0.21 # Tests async
```

---

## 2️⃣ Cambios en Configuración

### Antes (Config viejo)

```python
# src/config.py
class Config:
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 500000000))
    # Sin validación automática
```

### Después (Config refactorizado)

```python
# src/config_refactored.py
from src.config_refactored import settings

# Automáticamente validado y seguro
print(settings.UPLOAD_FOLDER)  # Type: Path
print(settings.MAX_FILE_SIZE)  # Validado: 1MB - 10GB
```

### Cambios en `.env`

Copia `.env.example` a `.env` y ajusta según tu entorno:

```bash
cp .env.example .env
```

---

## 3️⃣ Cambios en Excepciones

### Antes: Excepciones Genéricas

```python
# ❌ Viejo
if not target_format:
    return jsonify({'error': 'Format not specified'}), 400

if file_size > MAX_SIZE:
    return jsonify({'error': 'File too large'}), 413
```

### Después: Excepciones Específicas

```python
# ✅ Nuevo
from src.exceptions import (
    UnsupportedFormatException,
    FileTooLargeException
)

if not target_format:
    raise UnsupportedFormatException(
        target_format,
        supported_formats=get_allowed_extensions()
    )

if file_size > settings.MAX_FILE_SIZE:
    raise FileTooLargeException(file_size, max_size_mb)
```

### Respuesta Automática

Cuando levanta la excepción, se transforma automáticamente en:

```json
{
  "success": false,
  "error": "File too large: 600.50MB (maximum: 500.00MB)",
  "error_code": "FILE_TOO_LARGE",
  "timestamp": "2025-12-23T18:20:00.000000",
  "details": {
    "file_size_mb": 600.5,
    "max_size_mb": 500.0
  }
}
```

---

## 4️⃣ Cambios en Rutas (Routes)

### Cambios Principales

| Aspecto | Antes | Después |
|--------|--------|----------|
| **Config** | `from src.config import Config` | `from src.config_refactored import settings` |
| **Excepciones** | Generic `Exception` | Specific `FileConverterException` types |
| **Respuestas** | Sin campo `success` | Campo `success` obligatorio |
| **Logging** | `logger.info()` sin contexto | `logger.error(..., exc_info=True)` |
| **Validación** | Manual | Automática con Pydantic |

### Ejemplo Completo de Migración

**Antes:**

```python
@main_bp.route('/convert', methods=['POST'])
def convert_file():
    try:
        target_format = request.form.get('format', '').lower()
        
        if not target_format:
            logger.warning("Convert request without target format")
            return jsonify({'error': 'Target format not specified'}), 400
        
        file_size = file.size
        if file_size > Config.MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_size}")
            return jsonify({'error': f'File too large'}), 413
        
        # ... conversión ...
        return jsonify({'success': True, 'file_id': file_id}), 200
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

**Después:**

```python
@main_bp.route('/convert', methods=['POST'])
def convert_file():
    try:
        # Validar formato
        target_format = request.form.get('format', '').lower().strip()
        
        if not target_format or not is_allowed_extension(f"file.{target_format}"):
            raise UnsupportedFormatException(
                target_format,
                supported_formats=get_allowed_extensions()
            )
        
        # Validar tamaño
        file_size = get_file_size(source_path)
        if source_path.stat().st_size > settings.MAX_FILE_SIZE:
            raise FileTooLargeException(file_size, max_size_mb)
        
        # ... conversión ...
        return jsonify({
            'success': True,
            'file_id': file_id,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except FileConverterException as e:
        logger.warning(f"{e.error_code}: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Conversion failed',
            'error_code': 'CONVERSION_ERROR',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
```

---

## 5️⃣ Cambios en app.py

### Antes

```python
# ❌ Viejo
if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    app.run(debug=True)
```

### Después

```python
# ✅ Nuevo
from app_refactored import create_app, setup_cleanup_thread

if __name__ == '__main__':
    app = create_app()  # Factory pattern
    setup_cleanup_thread()  # Cleanup automático
    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )
```

---

## 6️⃣ Cambios en Imports

### Actualizar Todos los Imports

```python
# ❌ Viejo
from src.config import Config
from src.logging import logger  # si existe

# ✅ Nuevo
from src.config_refactored import settings
from src.logging import logger, get_logger
from src.exceptions import (
    FileConverterException,
    InvalidFileException,
    UnsupportedFormatException,
    # ...
)
from src.utils import (
    get_allowed_extensions,
    is_allowed_extension,
    get_file_size,
    sanitize_filename
)
```

---

## 7️⃣ Validar la Migración

### Paso 1: Revisar Logs

```bash
# Ver estructura de los nuevos logs
cat /tmp/file-converter/logs/file-converter-*.log | jq
```

### Paso 2: Validar Configuración

```bash
# Usar CLI command
flask validate-config

# Salida esperada:
# ✓ Configuration is valid
```

### Paso 3: Prueba Health Check

```bash
curl http://localhost:5000/health | jq

# Respuesta esperada:
{
  "success": true,
  "status": "healthy",
  "api": {
    "version": "2.0.0"
  }
}
```

### Paso 4: Probar Excepciones

```bash
# Sin formato
curl -X POST http://localhost:5000/convert \
  -F "file=@test.pdf"

# Respuesta:
{
  "success": false,
  "error": "Unsupported format: ",
  "error_code": "UNSUPPORTED_FORMAT",
  "timestamp": "2025-12-23T18:20:00.000000",
  "details": {
    "provided_format": "",
    "supported_formats": ["pdf", "docx", ...]
  }
}
```

---

## 8️⃣ Checklist de Migración

- [ ] Instalar nuevas dependencias (`pydantic`, `pydantic-settings`)
- [ ] Copiar `.env.example` a `.env`
- [ ] Actualizar `src/routes.py` (ya done en la rama)
- [ ] Actualizar `app.py` para usar `create_app()`
- [ ] Revisar imports en todos los archivos
- [ ] Reemplazar `Config.` con `settings.`
- [ ] Reemplazar excepciones genéricas con específicas
- [ ] Validar logs con formato JSON
- [ ] Ejecutar CLI: `flask validate-config`
- [ ] Probar health check
- [ ] Ejecutar tests locales
- [ ] Crear PR y hacer review

---

## 9️⃣ Troubleshooting

### Error: "No module named 'pydantic_settings'"

```bash
pip install pydantic-settings>=2.0.0
```

### Error: "settings is not defined"

Asegúrate de importar correctamente:

```python
from src.config_refactored import settings  # ✓ Correcto
from src.config import settings  # ✗ Incorrecto (no existe)
```

### Error: "Can't find UPLOAD_FOLDER"

El directorio se crea automáticamente. Si sigue fallando:

```bash
# Validar configuración
flask validate-config

# Crear manualmente
mkdir -p /tmp/file-converter/uploads
mkdir -p /tmp/file-converter/converted
mkdir -p /tmp/file-converter/logs
```

### Logs no en JSON

Verifica que `LOG_LEVEL` esté configurado en `.env`:

```bash
echo "LOG_LEVEL=INFO" >> .env
```

---

## 🔟 Verificación Final

Ejecuta este script para verificar todo:

```bash
#!/bin/bash

echo "✓ Validando configuración..."
flask validate-config || exit 1

echo "✓ Importando módulos..."
python -c "from src.exceptions import FileConverterException; print('OK')"
python -c "from src.config_refactored import settings; print(settings.ENV)"

echo "✓ Health check..."
curl -s http://localhost:5000/health | jq '.success' | grep true || exit 1

echo "✅ Migración completada exitosamente"
```

---

**Rama**: `refactor/phase-1`  
**Fecha**: 23 de diciembre, 2024  
**Versión**: 1.0.0
