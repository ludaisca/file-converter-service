# File Converter Microservice

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen)
![License MIT](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Descripción Ejecutiva

Microservicio API REST de alto rendimiento para la orquestación de conversiones de archivos multimedia. Proporciona una capa de abstracción unificada sobre herramientas especializadas como **FFmpeg**, **LibreOffice**, **ImageMagick** y **Tesseract OCR**, con capacidades avanzadas de caché y procesamiento asíncrono.

### ✨ Novedades v2.1.0

- ⚡ **Redis Cache**: Mejora de rendimiento hasta 10x para conversiones repetidas
- 💪 **Gunicorn Production Server**: Workers + threads para alta concurrencia
- 📈 **Métricas de Caché**: Endpoint `/cache/stats` con analítica en tiempo real
- 🔍 **Health Check Mejorado**: Monitoreo de Redis y métricas del sistema
- 📦 **Procesamiento Asíncrono**: Sistema de tareas con estado y tracking

## 🎯 Capacidades Técnicas

### Matriz de Conversión (v2.1.0)

Factory Pattern con delegación automática al motor más adecuado:

| Categoría | Formatos de Entrada | Formatos de Salida | Motor |
|-----------|---------------------|--------------------|-------|
| **Documentos** | `.docx`, `.doc`, `.odt`, `.rtf`, `.txt`, `.html`, `.xlsx`, `.xls`, `.csv`, `.ods`, `.pptx`, `.ppt`, `.odp` | `.pdf`, `.docx`, `.doc`, `.txt`, `.html`, `.odt`, `.rtf`, `.xlsx`, `.xls`, `.csv`, `.ods`, `.pptx`, `.ppt`, `.odp` | LibreOffice |
| **Imágenes** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`, `.heic`, `.avif`, `.ico`, `.psd`, `.xcf` | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tiff`, `.ico`, `.pdf`, `.svg` | ImageMagick |
| **Audio/Video** | `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`, `.webm`, `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`, `.aac`, `.opus`, `.wma` | `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.gif`, `.webp`, `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`, `.aac`, `.opus`, `.wma` | FFmpeg |
| **Archivos** | `.zip`, `.7z`, `.rar`, `.tar`, `.gz`, `.bz2`, `.xz` | `.zip`, `.7z`, `.tar`, `.tar.gz` | Built-in (7z/tar) |

### 📊 Sistema de Caché Inteligente

**Arquitectura:**
- **Storage**: Redis con política LRU (Least Recently Used)
- **Hash Key**: SHA-256 del archivo fuente + formato destino
- **TTL Configurable**: Default 24 horas (configurable vía `CACHE_TTL`)
- **Size Limit**: Archivos hasta 100MB (configurable vía `CACHE_MAX_SIZE`)

**Beneficios:**
- ⚡ **10x más rápido** para conversiones idénticas
- 💾 **Reducción de CPU**: Hasta 90% en workloads repetitivos
- 🔄 **Automatic Invalidation**: Expiración automática por TTL
- 📈 **Métricas**: Hit rate, miss rate, size, entries count

### 🔐 Seguridad y Arquitectura

- **Validación Estricta**: Magic numbers para detección MIME real
- **Sanitización**: UUIDs + `secure_filename` (prevención path traversal)
- **Rate Limiting**: Protección por IP con Redis backend
- **Configuración Tipada**: Pydantic para validación robusta
- **Health Checks**: Monitoreo continuo con Docker healthcheck

### 📦 OCR (Reconocimiento Óptico de Caracteres)

Extracción de texto de PDF escaneados e imágenes con:
- **Motor**: Tesseract OCR 5.x
- **Preprocesamiento**: Mejora automática de imagen
- **Idiomas**: Español, Inglés, Francés, Alemán, etc.
- **Confianza**: Score de precisión por extracción

## 🚀 Guía de Instalación y Despliegue

### Requisitos Previos

- Docker 20.x+
- Docker Compose 2.x+
- 2GB RAM mínimo (4GB recomendado)
- 2 CPU cores (4 cores recomendado)

### Despliegue Rápido con Docker Compose

```bash
# 1. Clonar repositorio
git clone https://github.com/ludaisca/file-converter-service.git
cd file-converter-service

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env según tus necesidades

# 3. Iniciar servicios
docker-compose up -d --build

# 4. Verificar estado
curl http://localhost:5000/health
```

El servicio estará disponible en `http://localhost:5000`.

### Arquitectura de Contenedores

```
┌────────────────────────┐
│  file-converter-api    │
│  (Gunicorn + Flask)    │
│  - 4 workers           │
│  - 2 threads/worker    │
│  - Port: 5000          │
└───────┬────────────────┘
       │
       │ depends_on
       │
       │
┌───────┴────────────────┐
│  file-converter-redis  │
│  (Redis 7 Alpine)      │
│  - MaxMemory: 256MB    │
│  - Policy: LRU         │
│  - Port: 6379          │
└────────────────────────┘
```

### ⚙️ Variables de Entorno Principales

#### Flask & App
```bash
FLASK_ENV=production          # Modo de Flask
FLASK_DEBUG=False             # Debug mode (NO en producción)
MAX_FILE_SIZE=52428800        # 50MB en bytes
```

#### Redis Cache
```bash
REDIS_ENABLED=true            # Habilitar caché
REDIS_HOST=redis              # Host (nombre del servicio)
REDIS_PORT=6379               # Puerto estándar
REDIS_DB=0                    # Base de datos (0-15)
REDIS_PASSWORD=               # Password (vacío = sin auth)
CACHE_TTL=86400               # 24 horas en segundos
CACHE_MAX_SIZE=104857600      # 100MB en bytes
```

#### Gunicorn (Producción)
```bash
GUNICORN_WORKERS=4                  # Workers (2x cores + 1)
GUNICORN_THREADS=2                  # Threads por worker
GUNICORN_TIMEOUT=300                # Timeout 5 minutos
GUNICORN_MAX_REQUESTS=1000          # Requests antes de reiniciar
GUNICORN_MAX_REQUESTS_JITTER=100    # Jitter aleatorio
```

#### OCR
```bash
ENABLE_OCR=true               # Habilitar OCR
OCR_DEFAULT_LANGUAGE=spa      # Idioma por defecto
OCR_MAX_PAGES=50              # Máx páginas en PDFs
```

Ver [.env.example](.env.example) para documentación completa.

## 📚 Documentación de la API

### Base URL
```
http://localhost:5000
```

### 1. Health Check
**GET** `/health`

Retorna estado del sistema, Redis y métricas.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "service": "file-converter",
  "version": "2.1.0",
  "cache": {
    "enabled": true,
    "connected": true,
    "latency_ms": 0.5
  },
  "timestamp": "2026-02-12T19:00:00Z"
}
```

### 2. Convertir Archivo
**POST** `/convert`

Conversión asíncrona con tracking de estado.

**Params (multipart/form-data):**
- `file`: Archivo binario (opcional)
- `url`: URL pública del archivo (opcional)
- `format`: Formato destino (ej: `pdf`, `mp3`)

**Response:**
```json
{
  "success": true,
  "message": "Conversion started",
  "task_id": "abc123...",
  "status_url": "/status/abc123...",
  "timestamp": "2026-02-12T19:00:00Z"
}
```

### 3. Estado de Tarea
**GET** `/status/<task_id>`

Consulta progreso de conversión.

**Response (Completado):**
```json
{
  "task_id": "abc123...",
  "status": "completed",
  "result": {
    "success": true,
    "file_id": "xyz789",
    "source_format": ".docx",
    "output_format": ".pdf",
    "output_size_mb": 1.2,
    "download_url": "/download/xyz789.pdf",
    "cached": false,
    "timestamp": "2026-02-12T19:01:00Z"
  },
  "submitted_at": "2026-02-12T19:00:00Z",
  "completed_at": "2026-02-12T19:01:00Z"
}
```

### 4. Estadísticas de Caché ✨ NUEVO
**GET** `/cache/stats`

Métricas de rendimiento del caché.

**Response:**
```json
{
  "success": true,
  "cache": {
    "enabled": true,
    "connected": true,
    "total_entries": 156,
    "memory_used_mb": 89.4,
    "hit_rate": 0.73,
    "miss_rate": 0.27,
    "total_hits": 1234,
    "total_misses": 456
  },
  "timestamp": "2026-02-12T19:00:00Z"
}
```

### 5. Limpiar Caché ✨ NUEVO
**POST** `/cache/clear`

Elimina todas las entradas del caché.

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared successfully",
  "entries_deleted": 156,
  "timestamp": "2026-02-12T19:00:00Z"
}
```

### 6. Extraer Texto (OCR)
**POST** `/extract-text`

Extracción de texto desde imágenes o PDFs.

**Params:**
- `file` o `url`
- `lang`: Código de idioma (`spa`, `eng`, `fra`)
- `preprocess`: `true`/`false` (mejora de imagen)

**Response:**
```json
{
  "success": true,
  "text": "Texto extraído del documento...",
  "confidence": 0.94,
  "language": "spa",
  "timestamp": "2026-02-12T19:00:00Z"
}
```

### 7. Descargar Archivo
**GET** `/download/<filename>`

Descarga el archivo convertido.

### 8. Formatos Soportados
**GET** `/formats`

Lista completa de conversiones disponibles.

### 9. Idiomas OCR
**GET** `/ocr/languages`

Idiomas disponibles para OCR.

## 📊 Monitoreo y Métricas

### Health Check Automation

```bash
# Docker Compose healthcheck (automático)
interval: 30s
timeout: 10s
retries: 3
start_period: 40s

# Consulta manual
curl http://localhost:5000/health
```

### Métricas de Caché

```bash
# Estadísticas detalladas
curl http://localhost:5000/cache/stats

# Verificar rendimiento
# Hit rate > 0.7 = Excelente
# Hit rate 0.4-0.7 = Bueno
# Hit rate < 0.4 = Considerar aumentar CACHE_TTL
```

### Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f file-converter

# Logs de Redis
docker-compose logs -f redis

# Logs desde archivo
tail -f logs/app.log
```

## 🛠️ Troubleshooting

### Redis no conecta

```bash
# Verificar que Redis esté corriendo
docker-compose ps redis

# Test de conexión
docker exec file-converter-redis redis-cli ping
# Debe responder: PONG

# Verificar logs
docker-compose logs redis
```

### Workers crashean

```bash
# Aumentar timeout en .env
GUNICORN_TIMEOUT=600  # 10 minutos

# Reducir workers si hay poco RAM
GUNICORN_WORKERS=2
```

### Conversiones lentas

```bash
# Aumentar workers (según CPU disponible)
GUNICORN_WORKERS=8  # Para servidor con 4 cores

# Verificar hit rate del caché
curl http://localhost:5000/cache/stats

# Si hit rate bajo, aumentar TTL
CACHE_TTL=604800  # 7 días
```

### Memory leaks

```bash
# Reducir max_requests para forzar reinicio más frecuente
GUNICORN_MAX_REQUESTS=500
GUNICORN_MAX_REQUESTS_JITTER=50

# Monitorear memoria de contenedor
docker stats file-converter-api
```

## 🔗 Integraciones

### n8n (Low-Code Automation)

```javascript
// Nodo HTTP Request en n8n
{
  "method": "POST",
  "url": "https://tu-dominio.com/convert",
  "bodyParameters": {
    "parameters": [
      {
        "name": "url",
        "value": "={{$json.file_url}}"
      },
      {
        "name": "format",
        "value": "pdf"
      }
    ]
  }
}
```

### cURL Examples

```bash
# Subir archivo local
curl -X POST http://localhost:5000/convert \
  -F "file=@documento.docx" \
  -F "format=pdf"

# Desde URL
curl -X POST http://localhost:5000/convert \
  -F "url=https://ejemplo.com/archivo.docx" \
  -F "format=pdf"

# OCR de imagen
curl -X POST http://localhost:5000/extract-text \
  -F "file=@imagen.jpg" \
  -F "lang=spa" \
  -F "preprocess=true"
```

## 💻 Stack Tecnológico

### Backend
- **Core**: Python 3.11, Flask 2.x
- **Production Server**: Gunicorn con workers + threads
- **Cache**: Redis 7 (Alpine)
- **Validation**: Pydantic para configuración tipada
- **Testing**: Pytest con coverage 85%

### Motores de Conversión
- **FFmpeg**: Audio/Video processing
- **LibreOffice**: Documentos (headless mode)
- **ImageMagick**: Imágenes y transformaciones
- **Tesseract OCR**: Extracción de texto
- **7zip**: Compresión/descompresión
- **Poppler**: PDF utilities

### DevOps
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Compatible con Kubernetes
- **CI/CD**: GitHub Actions ready
- **Monitoring**: Health checks + métricas

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

## 🤝 Contribuciones

Contribuciones son bienvenidas! Por favor:

1. Fork del repositorio
2. Crear branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/ludaisca/file-converter-service/issues)
- **Documentación**: [Wiki](https://github.com/ludaisca/file-converter-service/wiki)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

<p align="center">
  Desarrollado con ❤️ por <a href="https://github.com/ludaisca">Ludaisca</a>
</p>
