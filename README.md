# File Converter Service

Servicio de conversión de archivos desplegable con Docker Compose.

## 🚀 Características

- Conversión de documentos (DOCX, DOC, ODT → PDF, HTML, TXT)
- Conversión de imágenes (JPG, PNG, GIF, BMP → JPG, PNG, PDF, WebP)
- Conversión de video (MP4, AVI, MOV, MKV → MP4, AVI, GIF)
- Conversión de audio (MP3, WAV, OGG, M4A, FLAC → MP3, WAV, OGG)
- API REST simple y eficiente
- - Soporte de conversión desde URL (descarga automática de archivos remotos)
- Despliegue con Docker Compose

## 📋 Requisitos

- Docker
- Docker Compose

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/thecocoblue/file-converter-service.git
cd file-converter-service
```

2. Iniciar el servicio:
```bash
docker-compose up -d
```

3. Verificar que el servicio está corriendo:
```bash
curl http://localhost:5000/health
```

## 📖 Uso

### Verificar salud del servicio
```bash
curl http://localhost:5000/health
```

### Consultar formatos soportados
```bash
curl http://localhost:5000/formats
```

### Convertir un archivo
```bash
curl -X POST -F "file=@documento.docx" -F "format=pdf" \
  http://localhost:5000/convert
```

Respuesta:
```json
{
  "success": true,
  "file_id": "uuid-generado",
  "download_url": "/download/uuid-generado.pdf"
}
```

### Convertir desde URL

```bash
curl -X POST -F "url=https://ejemplo.com/archivo.m4a" -F "format=mp3" \
  http://localhost:5000/convert
```

Respuesta:

```json
{
  "success": true,
  "file_id": "uuid-generado",
  "output_format": "mp3",
  "download_url": "/download/uuid-generado.mp3"
}
```

### Descargar archivo convertido
```bash
curl -O http://localhost:5000/download/uuid-generado.pdf
```

## 🛠️ Configuración

Puedes modificar las variables de entorno en `docker-compose.yml`:

- `MAX_FILE_SIZE`: Tamaño máximo de archivo en MB (default: 50)
- `FLASK_ENV`: Entorno de Flask (production/development)

## 🏗️ Arquitectura

- **Flask**: Framework web para la API REST
- **LibreOffice**: Conversión de documentos
- **ImageMagick**: Conversión de imágenes
- **FFmpeg**: Conversión de audio y video
- **Pandoc**: Conversión avanzada de documentos

## 📝 API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/formats` | GET | Formatos soportados |
| `/convert` | POST | Convertir archivo |
| `/download/<filename>` | GET | Descargar archivo |

## 🔐 Seguridad

- Validación de tamaño de archivo
- Nombres de archivo seguros con UUID
- Limpieza automática de archivos temporales

## 📄 Licencia

MIT
