# 🔌 API Documentation

## Base URL

```
http://localhost:5000
```

En producción, reemplaza con tu dominio:
```
https://converter.tudominio.com
```

## 📦 Respuestas Comunes

### Estructura de Respuesta Exitosa

```json
{
  "success": true,
  "file_id": "string",
  "output_format": "string",
  "download_url": "string"
}
```

### Estructura de Respuesta de Error

```json
{
  "error": "string",
  "details": "string (opcional)"
}
```

### Códigos de Estado HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Solicitud exitosa |
| 400 | Bad Request | Parámetros inválidos o faltantes |
| 404 | Not Found | Archivo no encontrado |
| 413 | Payload Too Large | Archivo excede el tamaño máximo |
| 500 | Internal Server Error | Error en el servidor |

---

## 🟢 Endpoints

### 1. Health Check

Verifica el estado del servicio y obtiene métricas del sistema.

**Endpoint:** `GET /health`

**Parámetros:** Ninguno

**Respuesta Exitosa (200):**

```json
{
  "status": "healthy",
  "service": "file-converter",
  "timestamp": "2025-12-23T15:10:00.000Z",
  "uptime_seconds": 3600.5,
  "system": {
    "cpu_usage_percent": 2.5,
    "memory_usage_percent": 45.3,
    "memory_available_mb": 1024.5,
    "disk_usage_percent": 35.2,
    "disk_free_gb": 25.8
  },
  "api": {
    "version": "1.0.0",
    "upload_folder_exists": true,
    "converted_folder_exists": true,
    "logs_folder_exists": true
  }
}
```

**Respuesta de Error (500):**

```json
{
  "status": "unhealthy",
  "error": "System resource check failed"
}
```

**Ejemplos:**

```bash
# Bash/cURL
curl http://localhost:5000/health

# Python
import requests
response = requests.get('http://localhost:5000/health')
print(response.json())

# JavaScript/Node.js
fetch('http://localhost:5000/health')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

### 2. Obtener Formatos Soportados

Retorna todos los formatos de conversión soportados por tipo de archivo.

**Endpoint:** `GET /formats`

**Parámetros:** Ninguno

**Respuesta Exitosa (200):**

```json
{
  "documents": {
    "input": ["docx", "doc", "odt", "rtf"],
    "output": ["pdf", "html", "txt"]
  },
  "images": {
    "input": ["jpg", "jpeg", "png", "gif", "bmp"],
    "output": ["jpg", "png", "pdf", "webp"]
  },
  "video": {
    "input": ["mp4", "avi", "mov", "mkv"],
    "output": ["mp4", "avi", "gif"]
  },
  "audio": {
    "input": ["mp3", "wav", "ogg", "m4a", "flac"],
    "output": ["mp3", "wav", "ogg"]
  }
}
```

**Ejemplos:**

```bash
# Bash/cURL
curl http://localhost:5000/formats

# Python
import requests
formats = requests.get('http://localhost:5000/formats').json()
print(formats['documents']['output'])  # ['pdf', 'html', 'txt']

# JavaScript
const formats = await fetch('http://localhost:5000/formats').then(r => r.json());
console.log(formats.images.input);
```

---

### 3. Convertir Archivo

Convierte un archivo local o desde una URL a un formato especificado.

**Endpoint:** `POST /convert`

**Content-Type:** `multipart/form-data`

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `file` | File | Condicional* | Archivo a convertir (upload local) |
| `url` | String | Condicional* | URL del archivo a convertir |
| `format` | String | Sí | Formato de salida deseado |

*Nota: Debes proporcionar `file` O `url`, no ambos.

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "file_id": "a7b3c9d2e1f4",
  "output_format": "pdf",
  "download_url": "/download/a7b3c9d2e1f4.pdf"
}
```

**Errores Comunes:**

| Código | Mensaje | Causa |
|--------|---------|-------|
| 400 | `Target format not specified` | Falta el parámetro `format` |
| 400 | `Provide either "file" or "url"` | No se proporcionó archivo ni URL |
| 400 | `Empty URL provided` | URL vacía |
| 413 | `File too large. Maximum size is XMB` | Archivo excede MAX_FILE_SIZE |
| 500 | `Conversion failed: ...` | Error durante la conversión |

**Ejemplos:**

#### Convertir Archivo Local

```bash
# Bash/cURL - Convertir DOCX a PDF
curl -X POST \
  -F "file=@documento.docx" \
  -F "format=pdf" \
  http://localhost:5000/convert

# Bash/cURL - Convertir imagen a WebP
curl -X POST \
  -F "file=@imagen.jpg" \
  -F "format=webp" \
  http://localhost:5000/convert

# Bash/cURL - Convertir video a GIF
curl -X POST \
  -F "file=@video.mp4" \
  -F "format=gif" \
  http://localhost:5000/convert
```

```python
# Python con requests
import requests

# Convertir documento
with open('documento.docx', 'rb') as f:
    files = {'file': f}
    data = {'format': 'pdf'}
    response = requests.post(
        'http://localhost:5000/convert',
        files=files,
        data=data
    )
    result = response.json()
    print(f"Download: {result['download_url']}")

# Convertir audio
with open('audio.m4a', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/convert',
        files={'file': f},
        data={'format': 'mp3'}
    )
    print(response.json())
```

```javascript
// JavaScript/Node.js con FormData
const FormData = require('form-data');
const fs = require('fs');
const fetch = require('node-fetch');

const form = new FormData();
form.append('file', fs.createReadStream('documento.docx'));
form.append('format', 'pdf');

fetch('http://localhost:5000/convert', {
  method: 'POST',
  body: form
})
  .then(res => res.json())
  .then(data => console.log(data.download_url));
```

#### Convertir desde URL

```bash
# Bash/cURL
curl -X POST \
  -F "url=https://example.com/audio.m4a" \
  -F "format=mp3" \
  http://localhost:5000/convert
```

```python
# Python
import requests

response = requests.post(
    'http://localhost:5000/convert',
    data={
        'url': 'https://example.com/document.docx',
        'format': 'pdf'
    }
)
result = response.json()
if result['success']:
    print(f"File ID: {result['file_id']}")
    print(f"Download URL: {result['download_url']}")
```

```javascript
// JavaScript/Browser
const formData = new FormData();
formData.append('url', 'https://example.com/image.png');
formData.append('format', 'webp');

fetch('http://localhost:5000/convert', {
  method: 'POST',
  body: formData
})
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log('Download:', data.download_url);
    }
  });
```

---

### 4. Descargar Archivo Convertido

Descarga el archivo convertido usando el ID proporcionado.

**Endpoint:** `GET /download/<filename>`

**Parámetros de Ruta:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `filename` | String | Nombre del archivo (file_id + extensión) |

**Respuesta Exitosa (200):**

Binario del archivo con headers:
```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="<filename>"
```

**Errores:**

| Código | Mensaje | Causa |
|--------|---------|-------|
| 404 | `File not found` | Archivo no existe o fue eliminado |
| 500 | Error message | Error al leer el archivo |

**Ejemplos:**

```bash
# Bash/cURL - Descargar y guardar
curl -O http://localhost:5000/download/a7b3c9d2e1f4.pdf

# wget
wget http://localhost:5000/download/a7b3c9d2e1f4.pdf
```

```python
# Python - Descargar y guardar
import requests

file_id = 'a7b3c9d2e1f4'
format_ext = 'pdf'
filename = f"{file_id}.{format_ext}"

response = requests.get(f'http://localhost:5000/download/{filename}')
if response.status_code == 200:
    with open(f'downloaded_{filename}', 'wb') as f:
        f.write(response.content)
    print('File downloaded successfully')
else:
    print('Error:', response.json())
```

```javascript
// JavaScript/Browser - Descargar en navegador
function downloadFile(fileId, format) {
  const url = `http://localhost:5000/download/${fileId}.${format}`;
  
  // Opción 1: Abrir en nueva ventana
  window.open(url, '_blank');
  
  // Opción 2: Descargar con fetch
  fetch(url)
    .then(res => res.blob())
    .then(blob => {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${fileId}.${format}`;
      a.click();
    });
}
```

---

## 📑 Flujo Completo de Conversión

### Ejemplo: Convertir DOCX a PDF

```python
import requests
import time

# 1. Verificar que el servicio está disponible
health = requests.get('http://localhost:5000/health').json()
if health['status'] != 'healthy':
    print('Service is not healthy!')
    exit(1)

# 2. Verificar formatos soportados
formats = requests.get('http://localhost:5000/formats').json()
if 'pdf' not in formats['documents']['output']:
    print('PDF conversion not supported!')
    exit(1)

# 3. Convertir archivo
with open('documento.docx', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/convert',
        files={'file': f},
        data={'format': 'pdf'}
    )

if response.status_code != 200:
    print('Conversion failed:', response.json())
    exit(1)

result = response.json()
print(f"Conversion successful! File ID: {result['file_id']}")

# 4. Descargar archivo convertido
time.sleep(1)  # Esperar a que termine la conversión

download_url = f"http://localhost:5000{result['download_url']}"
download_response = requests.get(download_url)

if download_response.status_code == 200:
    with open('documento_convertido.pdf', 'wb') as f:
        f.write(download_response.content)
    print('File downloaded successfully!')
else:
    print('Download failed:', download_response.json())
```

---

## 🔍 Ejemplos de Integración

### Integración con n8n

```json
{
  "nodes": [
    {
      "name": "HTTP Request",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://file-converter:5000/convert",
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
      }
    }
  ]
}
```

### Integración con WhatsApp Business API

```python
# Recibir documento de WhatsApp y convertir a PDF
import requests

def convert_whatsapp_document(media_url, wa_token):
    # 1. Descargar archivo de WhatsApp
    headers = {'Authorization': f'Bearer {wa_token}'}
    media = requests.get(media_url, headers=headers).content
    
    # 2. Guardar temporalmente
    with open('temp_doc.docx', 'wb') as f:
        f.write(media)
    
    # 3. Convertir a PDF
    with open('temp_doc.docx', 'rb') as f:
        response = requests.post(
            'http://localhost:5000/convert',
            files={'file': f},
            data={'format': 'pdf'}
        )
    
    result = response.json()
    
    # 4. Obtener archivo convertido
    pdf_url = f"http://localhost:5000{result['download_url']}"
    
    return pdf_url
```

### Script Bash para Conversión Batch

```bash
#!/bin/bash
# convert_batch.sh - Convertir múltiples archivos

FORMAT="pdf"
INPUT_DIR="./input"
OUTPUT_DIR="./output"

mkdir -p "$OUTPUT_DIR"

for file in "$INPUT_DIR"/*; do
    echo "Converting: $file"
    
    response=$(curl -s -X POST \
        -F "file=@$file" \
        -F "format=$FORMAT" \
        http://localhost:5000/convert)
    
    file_id=$(echo $response | jq -r '.file_id')
    download_url=$(echo $response | jq -r '.download_url')
    
    if [ "$file_id" != "null" ]; then
        curl -s "http://localhost:5000$download_url" \
            -o "$OUTPUT_DIR/${file_id}.$FORMAT"
        echo "  ✓ Converted: ${file_id}.$FORMAT"
    else
        echo "  ✗ Failed: $file"
    fi
done

echo "Batch conversion completed!"
```

---

## ⚡ Rate Limiting

Actualmente el servicio **no implementa rate limiting**. Para producción, se recomienda:

1. Usar Nginx con `limit_req_zone`
2. Implementar Redis para rate limiting
3. Usar un API Gateway (Kong, Traefik)

---

## 🔒 Autenticación

Actualmente el servicio **no requiere autenticación**. Para producción:

1. Implementar API Keys
2. Usar JWT tokens
3. Configurar OAuth2

---

## 📊 Mejores Prácticas

1. **Siempre verificar el health check** antes de enviar conversiones
2. **Validar formatos soportados** usando `/formats`
3. **Implementar reintentos** con backoff exponencial
4. **Limpiar archivos descargados** después de usarlos
5. **Monitorear el tamaño de archivos** antes de enviarlos
6. **Usar timeouts apropiados** (60s para conversiones grandes)
7. **Cachear la respuesta de `/formats`** para evitar llamadas innecesarias

---

## 🐛 Reporte de Errores

Si encuentras un error en la API, por favor reporta:

1. Endpoint usado
2. Parámetros enviados
3. Respuesta recibida
4. Logs del servidor (si tienes acceso)

Crea un issue en: https://github.com/thecocoblue/file-converter-service/issues