# Documentación de la API

Referencia completa de la API del Servicio de Conversión de Archivos.

**URL Base**: `http://localhost:5000` (desarrollo) o tu dominio desplegado

**Versión de API**: `1.0.0`

---

## Tabla de Contenidos

- [Verificación de Salud](#verificación-de-salud)
- [Formatos Soportados](#formatos-soportados)
- [Convertir Archivo](#convertir-archivo)
- [Descargar Archivo](#descargar-archivo)
- [Respuestas de Error](#respuestas-de-error)

---

## Verificación de Salud

Verifica el estado del servicio y métricas del sistema.

### Endpoint
```
GET /health
```

### Respuesta (200 OK)
```json
{
  "status": "healthy",
  "service": "file-converter",
  "timestamp": "2024-12-23T15:30:00.000Z",
  "uptime_seconds": 3600.5,
  "system": {
    "cpu_usage_percent": 5.2,
    "memory_usage_percent": 45.8,
    "memory_available_mb": 2048.5,
    "disk_usage_percent": 35.2,
    "disk_free_gb": 50.3
  },
  "api": {
    "version": "1.0.0",
    "upload_folder_exists": true,
    "converted_folder_exists": true,
    "logs_folder_exists": true
  }
}
```

### Ejemplo
```bash
curl http://localhost:5000/health
```

---

## Formatos Soportados

Obtiene todos los formatos de conversión soportados.

### Endpoint
```
GET /formats
```

### Respuesta (200 OK)
```json
{
  "document": {
    "from": [".docx", ".doc", ".odt", ".rtf", ".txt"],
    "to": [".pdf", ".docx", ".txt", ".html"]
  },
  "image": {
    "from": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
    "to": [".jpg", ".png", ".pdf", ".webp"]
  },
  "video": {
    "from": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"],
    "to": [".mp4", ".avi", ".gif"]
  },
  "audio": {
    "from": [".mp3", ".wav", ".ogg", ".m4a", ".flac"],
    "to": [".mp3", ".wav", ".ogg"]
  }
}
```

### Ejemplo
```bash
curl http://localhost:5000/formats
```

---

## Convertir Archivo

Convierte un archivo subiéndolo o proporcionando una URL.

### Endpoint
```
POST /convert
```

### Métodos de Solicitud

#### Método 1: Subir Archivo

**Parámetros** (multipart/form-data):
- `file` (requerido): Archivo a convertir
- `format` (requerido): Formato destino (sin punto, ej: "pdf")

**Ejemplo**:
```bash
curl -X POST \
  -F "file=@documento.docx" \
  -F "format=pdf" \
  http://localhost:5000/convert
```

#### Método 2: Descargar desde URL

**Parámetros** (multipart/form-data):
- `url` (requerido): URL del archivo a descargar y convertir
- `format` (requerido): Formato destino (sin punto, ej: "mp3")

**Ejemplo**:
```bash
curl -X POST \
  -F "url=https://ejemplo.com/audio.m4a" \
  -F "format=mp3" \
  http://localhost:5000/convert
```

### Respuesta (200 OK)
```json
{
  "success": true,
  "file_id": "a1b2c3d4e5f6",
  "output_format": "pdf",
  "download_url": "/download/a1b2c3d4e5f6.pdf"
}
```

### Respuestas de Error

#### 400 Bad Request - Sin formato especificado
```json
{
  "error": "Target format not specified"
}
```

#### 400 Bad Request - Sin archivo o URL
```json
{
  "error": "Provide either \"file\" or \"url\""
}
```

#### 400 Bad Request - URL vacía
```json
{
  "error": "Empty URL provided"
}
```

#### 413 Payload Too Large - Archivo muy grande
```json
{
  "error": "File too large. Maximum size is 50MB"
}
```

#### 500 Internal Server Error - Conversión fallida
```json
{
  "error": "Conversion from .docx to .pdf is not supported"
}
```

---

## Descargar Archivo

Descarga un archivo convertido.

### Endpoint
```
GET /download/<filename>
```

### Parámetros
- `filename` (parámetro de ruta): El nombre del archivo de la respuesta de conversión

### Respuesta
- **200 OK**: Devuelve el archivo como adjunto
- **404 Not Found**: El archivo no existe o fue eliminado

### Ejemplo
```bash
# Obtener la URL de descarga de la respuesta de conversión
curl -O http://localhost:5000/download/a1b2c3d4e5f6.pdf

# O con nombre de salida personalizado
curl -o miarchivo.pdf http://localhost:5000/download/a1b2c3d4e5f6.pdf
```

### Respuesta de Error (404)
```json
{
  "error": "File not found"
}
```

---

## Respuestas de Error

Todas las respuestas de error siguen este formato:

```json
{
  "error": "Mensaje de descripción del error"
}
```

### Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200    | Éxito |
| 400    | Solicitud Incorrecta - Parámetros inválidos |
| 404    | No Encontrado - El archivo no existe |
| 413    | Carga Muy Grande - El archivo excede el límite |
| 500    | Error Interno del Servidor - Error de conversión o sistema |

---

## Limitación de Tasa

Actualmente no hay limitación de tasa implementada. Considera implementar rate limiting para despliegues en producción.

---

## Ciclo de Vida del Archivo

1. **Subida/Descarga**: El archivo se guarda en `/app/uploads`
2. **Conversión**: El archivo se convierte y se guarda en `/app/converted`
3. **Descarga**: El archivo convertido está disponible para descarga
4. **Limpieza**: Los archivos se eliminan automáticamente después de `FILE_TTL` segundos (por defecto: 3600s)

**Nota**: Descarga tus archivos convertidos dentro de la ventana de TTL o serán eliminados.

---

## Compresión GZIP

La API comprime automáticamente las respuestas cuando el cliente lo soporta.

### Solicitud con compresión
```bash
curl -H "Accept-Encoding: gzip" http://localhost:5000/formats
```

---

## Ejemplos de Integración

### Python
```python
import requests

# Subir y convertir
files = {'file': open('documento.docx', 'rb')}
data = {'format': 'pdf'}
response = requests.post('http://localhost:5000/convert', files=files, data=data)
result = response.json()

# Descargar archivo convertido
download_url = f"http://localhost:5000{result['download_url']}"
converted = requests.get(download_url)
with open('salida.pdf', 'wb') as f:
    f.write(converted.content)
```

### JavaScript (fetch)
```javascript
// Subir y convertir
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('format', 'pdf');

const response = await fetch('http://localhost:5000/convert', {
  method: 'POST',
  body: formData
});

const result = await response.json();

// Descargar
window.location.href = `http://localhost:5000${result.download_url}`;
```

### cURL Avanzado
```bash
# Convertir y guardar en un solo comando
RESPONSE=$(curl -s -F "file=@entrada.docx" -F "format=pdf" http://localhost:5000/convert)
DOWNLOAD_URL=$(echo $RESPONSE | jq -r '.download_url')
curl -o salida.pdf "http://localhost:5000$DOWNLOAD_URL"
```

### n8n Workflow
```json
{
  "nodes": [
    {
      "parameters": {
        "url": "http://localhost:5000/convert",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "format",
              "value": "pdf"
            }
          ]
        },
        "sendBinaryData": true,
        "binaryPropertyName": "data"
      },
      "name": "Convertir Archivo",
      "type": "n8n-nodes-base.httpRequest",
      "position": [250, 300]
    }
  ]
}
```

---

## Soporte

Para problemas o preguntas, visita el [repositorio de GitHub](https://github.com/thecocoblue/file-converter-service).
