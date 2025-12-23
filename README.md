# 🔄 File Converter Service

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)

Servicio de conversión de archivos multimedia desplegable con Docker Compose. API REST simple, rápida y eficiente para convertir documentos, imágenes, audio y video.

## 🚀 Características

- **Conversión de Documentos**: DOCX, DOC, ODT → PDF, HTML, TXT
- **Conversión de Imágenes**: JPG, PNG, GIF, BMP → JPG, PNG, PDF, WebP
- **Conversión de Video**: MP4, AVI, MOV, MKV → MP4, AVI, GIF
- **Conversión de Audio**: MP3, WAV, OGG, M4A, FLAC → MP3, WAV, OGG
- **API REST**: Endpoints simples y bien documentados
- **Conversión desde URL**: Descarga automática de archivos remotos
- **Health Monitoring**: Sistema de monitoreo de salud con métricas
- **Logging Estructurado**: Sistema de logs rotativos y consultables
- **Compresión Gzip**: Respuestas comprimidas automáticamente
- **Docker Ready**: Despliegue con un solo comando

## 📋 Requisitos

- Docker >= 20.10
- Docker Compose >= 2.0
- 2GB RAM mínimo
- 10GB espacio en disco

## 🔧 Instalación

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/thecocoblue/file-converter-service.git
cd file-converter-service

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env según tus necesidades

# 3. Iniciar el servicio
docker-compose up -d

# 4. Verificar que está funcionando
curl http://localhost:5000/health
```

### Configuración Avanzada

Edita el archivo `.env` para personalizar:

```env
# Tamaño máximo de archivo (en MB)
MAX_FILE_SIZE=50

# Entorno de Flask
FLASK_ENV=production

# Puerto del servicio
PORT=5000

# Nivel de logging (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

## 📖 Uso de la API

### 1. Health Check

Verifica el estado del servicio y métricas del sistema:

```bash
curl http://localhost:5000/health
```

**Respuesta:**
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

### 2. Consultar Formatos Soportados

```bash
curl http://localhost:5000/formats
```

**Respuesta:**
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

### 3. Convertir Archivo Local

```bash
curl -X POST \
  -F "file=@documento.docx" \
  -F "format=pdf" \
  http://localhost:5000/convert
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "file_id": "a7b3c9d2e1f4",
  "output_format": "pdf",
  "download_url": "/download/a7b3c9d2e1f4.pdf"
}
```

### 4. Convertir desde URL

```bash
curl -X POST \
  -F "url=https://example.com/audio.m4a" \
  -F "format=mp3" \
  http://localhost:5000/convert
```

**Respuesta:**
```json
{
  "success": true,
  "file_id": "b8c4d3e2f1a5",
  "output_format": "mp3",
  "download_url": "/download/b8c4d3e2f1a5.mp3"
}
```

### 5. Descargar Archivo Convertido

```bash
# Usando curl
curl -O http://localhost:5000/download/a7b3c9d2e1f4.pdf

# O con wget
wget http://localhost:5000/download/a7b3c9d2e1f4.pdf
```

## 🛠️ Configuración

### Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `MAX_FILE_SIZE` | 50 | Tamaño máximo de archivo en MB |
| `FLASK_ENV` | production | Entorno de Flask (production/development) |
| `PORT` | 5000 | Puerto donde escucha el servicio |
| `LOG_LEVEL` | INFO | Nivel de logging (DEBUG/INFO/WARNING/ERROR) |

### Volúmenes Docker

```yaml
volumes:
  - ./uploads:/app/uploads        # Archivos temporales subidos
  - ./converted:/app/converted    # Archivos convertidos
  - ./logs:/app/logs              # Logs del sistema
```

## 🏗️ Arquitectura

### Stack Tecnológico

- **Flask**: Framework web para la API REST
- **LibreOffice**: Conversión de documentos de oficina
- **ImageMagick**: Procesamiento y conversión de imágenes
- **FFmpeg**: Conversión de audio y video
- **Pandoc**: Conversión avanzada de documentos
- **psutil**: Monitoreo de sistema
- **Gunicorn**: WSGI server para producción

### Estructura del Proyecto

```
file-converter-service/
├── app.py                 # Punto de entrada
├── src/
│   ├── config.py         # Configuración centralizada
│   ├── routes.py         # Endpoints de la API
│   ├── utils.py          # Utilidades compartidas
│   ├── logging.py        # Sistema de logging
│   └── converters/       # Módulos de conversión
│       ├── factory.py    # Factory pattern
│       ├── document.py   # Conversión de documentos
│       ├── image.py      # Conversión de imágenes
│       ├── video.py      # Conversión de video
│       └── audio.py      # Conversión de audio
├── tests/                # Suite de pruebas
├── Dockerfile            # Imagen Docker
├── docker-compose.yml    # Orquestación
└── requirements.txt      # Dependencias Python
```

## 📝 API Endpoints

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/health` | GET | Health check con métricas del sistema | No |
| `/formats` | GET | Lista de formatos soportados | No |
| `/convert` | POST | Convertir archivo (local o URL) | No |
| `/download/<filename>` | GET | Descargar archivo convertido | No |

Para documentación detallada de la API, consulta [API.md](./API.md).

## 🔐 Seguridad

- ✅ Validación de tamaño de archivo configurable
- ✅ Nombres de archivo seguros con UUID
- ✅ Limpieza automática de archivos temporales
- ✅ Sanitización de nombres de archivo
- ✅ Validación de extensiones permitidas
- ✅ Sin ejecución de código arbitrario
- ✅ Logs sin datos sensibles

## 🐛 Troubleshooting

### El servicio no inicia

```bash
# Verificar logs
docker-compose logs file-converter

# Verificar puertos en uso
lsof -i :5000

# Reconstruir imagen
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Conversión falla

```bash
# Verificar que el archivo existe
ls -la uploads/

# Verificar logs de conversión
docker-compose logs file-converter | grep ERROR

# Verificar espacio en disco
df -h
```

### Error "File too large"

Aumenta el límite en `.env`:
```env
MAX_FILE_SIZE=100
```

Luego reinicia:
```bash
docker-compose restart
```

### Health check retorna "unhealthy"

```bash
# Verificar recursos del sistema
docker stats file-converter

# Verificar espacio en disco
docker exec file-converter df -h

# Revisar logs
docker-compose logs file-converter --tail 100
```

## 📊 Monitoreo

### Logs

Los logs se guardan en `./logs/app.log` con rotación automática:

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Buscar errores
grep ERROR logs/app.log

# Ver logs de Docker
docker-compose logs -f file-converter
```

### Métricas

Consulta `/health` para métricas en tiempo real:
- CPU usage
- Memoria disponible
- Uso de disco
- Estado de carpetas

## 🚀 Despliegue en Producción

Ver [DEPLOYMENT.md](./DEPLOYMENT.md) para:
- Despliegue en Coolify
- Configuración de Nginx como reverse proxy
- SSL/TLS con Let's Encrypt
- Escalado horizontal
- Backup y recuperación

## 🧪 Testing

```bash
# Ejecutar tests
python -m pytest tests/

# Con cobertura
python -m pytest tests/ --cov=src

# Tests específicos
python -m pytest tests/test_converters.py
```

## 📈 Roadmap

- [ ] Autenticación con API keys
- [ ] Rate limiting
- [ ] Cola de trabajos con Redis
- [ ] Webhooks para notificaciones
- [ ] Conversión batch de múltiples archivos
- [ ] OCR para PDFs escaneados
- [ ] Watermarking de imágenes
- [ ] Compresión de archivos convertidos

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**thecocoblue**

- GitHub: [@thecocoblue](https://github.com/thecocoblue)

## 🙏 Agradecimientos

- LibreOffice por el excelente soporte de conversión de documentos
- FFmpeg por las capacidades multimedia
- ImageMagick por el procesamiento de imágenes
- La comunidad de Docker por las mejores prácticas

---

⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub!