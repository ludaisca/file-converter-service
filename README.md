# 🔄 File Converter Service

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Versión](https://img.shields.io/badge/versión-1.0.0-blue.svg)](https://github.com/thecocoblue/file-converter-service/releases)

Servicio de conversión de archivos multimedia desplegable con Docker. API REST simple, rápida y eficiente para convertir documentos, imágenes, audio y video.

---

## 📚 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación Rápida](#-instalación-rápida)
- [Uso de la API](#-uso-de-la-api)
- [Configuración](#-configuración)
- [Arquitectura](#-arquitectura)
- [Documentación](#-documentación)
- [Despliegue](#-despliegue)
- [Seguridad](#-seguridad)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## 🚀 Características

### Conversiones Soportadas

- **📄 Documentos**: DOCX, DOC, ODT, RTF, TXT → PDF, HTML, TXT, DOCX
- **🖼️ Imágenes**: JPG, PNG, GIF, BMP, TIFF, WebP → JPG, PNG, PDF, WebP
- **🎥 Video**: MP4, AVI, MOV, MKV, FLV, WMV → MP4, AVI, GIF
- **🎵 Audio**: MP3, WAV, OGG, M4A, FLAC → MP3, WAV, OGG

### Características Principales

- ✅ **API REST** simple y bien documentada
- ✅ **Conversión desde URL** - Descarga automática de archivos remotos
- ✅ **Health Monitoring** - Métricas del sistema (CPU, RAM, disco)
- ✅ **Logging Estructurado** - Sistema de logs con niveles configurables
- ✅ **Compresión GZIP** - Respuestas comprimidas automáticamente
- ✅ **Limpieza Automática** - Gestión de archivos temporales con TTL configurable
- ✅ **Docker Ready** - Despliegue con un solo comando
- ✅ **Healthcheck Integrado** - Monitoreo de contenedor
- ✅ **Seguridad** - Validación de archivos, nombres seguros con UUID
- ✅ **Sin Dependencias Externas** - Todo incluido en el contenedor

---

## 📋 Requisitos

### Mínimos
- Docker >= 20.10
- Docker Compose >= 2.0
- 512 MB RAM
- 2 GB espacio en disco

### Recomendados
- 1 GB RAM
- 10 GB espacio en disco
- CPU con 2+ cores
- SSD para mejor rendimiento

---

## ⚡ Instalación Rápida

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/thecocoblue/file-converter-service.git
cd file-converter-service

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env según tus necesidades (opcional)

# 3. Iniciar el servicio
docker-compose up -d

# 4. Verificar que está funcionando
curl http://localhost:5000/health
```

### Opción 2: Coolify

Ver [guía completa de despliegue en Coolify](docs/DEPLOYMENT.md#despliegue-en-coolify).

### Opción 3: Manual

Ver [guía de despliegue manual](docs/DEPLOYMENT.md#despliegue-manual).

---

## 💻 Uso de la API

### 1. Verificar Salud del Servicio

Obtiene métricas del sistema en tiempo real:

```bash
curl http://localhost:5000/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "file-converter",
  "timestamp": "2024-12-23T15:10:00.000Z",
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

### 3. Convertir Archivo (Subida Local)

```bash
curl -X POST \
  -F "file=@documento.docx" \
  -F "format=pdf" \
  http://localhost:5000/convert
```

**Respuesta:**
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
  -F "url=https://ejemplo.com/audio.m4a" \
  -F "format=mp3" \
  http://localhost:5000/convert
```

### 5. Descargar Archivo Convertido

```bash
# Con curl
curl -O http://localhost:5000/download/a7b3c9d2e1f4.pdf

# Con wget
wget http://localhost:5000/download/a7b3c9d2e1f4.pdf
```

### Ejemplos de Integración

#### Python
```python
import requests

# Convertir archivo
files = {'file': open('documento.docx', 'rb')}
data = {'format': 'pdf'}
response = requests.post('http://localhost:5000/convert', files=files, data=data)
result = response.json()

# Descargar
download_url = f"http://localhost:5000{result['download_url']}"
converted = requests.get(download_url)
with open('salida.pdf', 'wb') as f:
    f.write(converted.content)
```

#### n8n Workflow
```json
{
  "nodes": [
    {
      "parameters": {
        "url": "http://localhost:5000/convert",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [{"name": "format", "value": "pdf"}]
        },
        "sendBinaryData": true
      },
      "name": "Convertir Archivo",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

Para más ejemplos, ver [docs/API.md](docs/API.md#ejemplos-de-integración).

---

## ⚙️ Configuración

### Variables de Entorno

#### Configuración Básica

| Variable | Default | Descripción |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Entorno de Flask (`production`/`development`) |
| `MAX_FILE_SIZE` | `50` | Tamaño máximo de archivo en MB |
| `MAX_DOWNLOAD_SIZE` | `100` | Tamaño máximo de descarga en MB |

#### Configuración Avanzada

| Variable | Default | Descripción |
|----------|---------|-------------|
| `CLEANUP_INTERVAL` | `3600` | Intervalo de limpieza en segundos |
| `FILE_TTL` | `3600` | Tiempo de vida de archivos en segundos |
| `LOG_LEVEL` | `INFO` | Nivel de logging (DEBUG/INFO/WARNING/ERROR) |
| `LOG_FILE` | `/app/logs/app.log` | Ruta del archivo de log |
| `ENABLE_HEALTH_MONITORING` | `True` | Habilitar monitoreo de salud |
| `API_VERSION` | `1.0.0` | Versión de la API |

#### Rutas de Directorios

| Variable | Default | Descripción |
|----------|---------|-------------|
| `UPLOAD_FOLDER` | `/app/uploads` | Directorio de archivos subidos |
| `CONVERTED_FOLDER` | `/app/converted` | Directorio de archivos convertidos |
| `LOGS_FOLDER` | `/app/logs` | Directorio de logs |

### Ejemplo de .env para Producción

```bash
# Flask
FLASK_ENV=production
FLASK_DEBUG=False

# Límites de archivos
MAX_FILE_SIZE=100        # 100 MB para archivos grandes
MAX_DOWNLOAD_SIZE=200    # 200 MB para descargas

# Limpieza cada 30 minutos
CLEANUP_INTERVAL=1800
FILE_TTL=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# Monitoreo
ENABLE_HEALTH_MONITORING=True
```

Para más detalles, ver [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#variables-de-entorno).

---

## 🏗️ Arquitectura

### Stack Tecnológico

- **Flask**: Framework web para la API REST
- **LibreOffice**: Conversión de documentos de oficina
- **ImageMagick**: Procesamiento y conversión de imágenes
- **FFmpeg**: Conversión de audio y video
- **Pandoc**: Conversión avanzada de documentos
- **psutil**: Monitoreo de métricas del sistema

### Estructura del Proyecto

```
file-converter-service/
├── app.py                    # Punto de entrada
├── src/
│   ├── config.py            # Configuración centralizada
│   ├── routes.py            # Endpoints de la API
│   ├── utils.py             # Utilidades (descarga, limpieza)
│   ├── logging.py           # Sistema de logging
│   └── converters/          # Módulos de conversión
│       ├── base.py          # Clase base abstracta
│       ├── factory.py       # Factory pattern
│       ├── libreoffice.py   # Conversor de documentos
│       ├── imagemagick.py   # Conversor de imágenes
│       └── ffmpeg.py        # Conversor de audio/video
├── tests/                   # Suite de pruebas
├── docs/                    # Documentación
│   ├── API.md               # Documentación de API
│   ├── DEPLOYMENT.md        # Guía de despliegue
│   └── TROUBLESHOOTING.md   # Solución de problemas
├── Dockerfile               # Imagen Docker
├── docker-compose.yml       # Orquestación
├── requirements.txt         # Dependencias Python
├── .env.example             # Template de configuración
├── LICENSE                  # Licencia MIT
├── CHANGELOG.md             # Historial de versiones
├── SECURITY.md              # Políticas de seguridad
└── CONTRIBUTING.md          # Guía de contribución
```

### Flujo de Conversión
```
1. Request → Validación de parámetros
2. Upload/Download → Guardar en /app/uploads
3. Validación de tamaño y extensión
4. Factory → Seleccionar conversor apropiado
5. Conversión → Procesar archivo
6. Guardar en /app/converted
7. Limpieza de archivo original
8. Response → URL de descarga
9. Background cleanup → Eliminar después de TTL
```

---

## 📚 Documentación

### Documentos Disponibles

- **[API.md](docs/API.md)** - Documentación completa de la API REST
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Guía de despliegue (Docker, Coolify, Manual)
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Solución de problemas comunes
- **[SECURITY.md](SECURITY.md)** - Políticas de seguridad
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guía para contribuidores
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios

### API Endpoints

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/health` | GET | Health check con métricas del sistema | No |
| `/formats` | GET | Lista de formatos soportados | No |
| `/convert` | POST | Convertir archivo (local o URL) | No |
| `/download/<filename>` | GET | Descargar archivo convertido | No |

Para documentación detallada, ver [docs/API.md](docs/API.md).

---

## 🚀 Despliegue

### Docker Compose (Local/Servidor)

```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Actualizar
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Coolify (Recomendado para Producción)

1. En Coolify: **+ New Resource** → **Docker Compose**
2. Repository: `https://github.com/thecocoblue/file-converter-service.git`
3. Configurar variables de entorno
4. Configurar dominio y SSL
5. Deploy

Ver [guía completa en docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#despliegue-en-coolify).

### Proxy Reverso (Nginx/Traefik)

Ver ejemplos de configuración en [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#configuración-de-proxy-reverso).

---

## 🔒 Seguridad

### Medidas Implementadas

- ✅ Sanitización de nombres de archivo con `secure_filename()`
- ✅ Nombres únicos con UUID para evitar colisiones
- ✅ Validación de tamaño de archivos (configurable)
- ✅ Timeout de 30 segundos en descargas desde URL
- ✅ Stream processing para evitar saturar memoria
- ✅ Limpieza automática de archivos temporales
- ✅ Política de ImageMagick modificada para PDFs seguros
- ✅ Logging sin datos sensibles

### Recomendaciones para Producción

- ⚠️ **Usar HTTPS siempre** (Coolify lo configura automáticamente)
- ⚠️ **Implementar autenticación** (API keys, Basic Auth, o VPN)
- ⚠️ **Configurar rate limiting** en proxy reverso
- ⚠️ **No exponer puerto 5000 directamente** a internet
- ⚠️ **Configurar firewall** correctamente
- ⚠️ **Monitorear logs** regularmente

Ver [SECURITY.md](SECURITY.md) para detalles completos.

---

## 🐛 Troubleshooting

### Problemas Comunes

#### El servicio no inicia

```bash
# Ver logs
docker-compose logs file-converter

# Verificar puertos
lsof -i :5000

# Reconstruir
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Error "File too large"

Edita `.env`:
```bash
MAX_FILE_SIZE=100  # Aumentar a 100 MB
```

Reinicia:
```bash
docker-compose restart
```

#### Conversiones fallan

```bash
# Ver logs detallados
docker exec -it file-converter-api tail -f /app/logs/app.log

# Verificar herramientas instaladas
docker exec -it file-converter-api which libreoffice
docker exec -it file-converter-api which ffmpeg
```

Ver [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) para más soluciones.

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/

# Con cobertura
python -m pytest tests/ --cov=src

# Tests específicos
python -m pytest tests/test_converters.py -v
```

---

## 📊 Monitoreo

### Logs

```bash
# Logs en tiempo real
tail -f logs/app.log

# Buscar errores
grep ERROR logs/app.log

# Logs de Docker
docker-compose logs -f file-converter
```

### Métricas

```bash
# Health check
curl http://localhost:5000/health | jq

# Estadísticas de Docker
docker stats file-converter-api
```

---

## 🗺️ Roadmap

### Versión 1.1.0 (Planeada)

- [ ] Autenticación con API keys
- [ ] Rate limiting integrado
- [ ] Queue system con Redis
- [ ] Webhooks para notificaciones

### Versión 1.2.0 (Futuro)

- [ ] Conversión batch de múltiples archivos
- [ ] OCR para PDFs escaneados
- [ ] Watermarking de imágenes
- [ ] Parámetros de calidad configurables
- [ ] Interfaz web simple

### Ideas de la Comunidad

- [ ] Soporte para más formatos (EPUB, MOBI, etc.)
- [ ] Compresión de archivos convertidos
- [ ] Edición básica de imágenes (resize, crop)
- [ ] Extracción de texto de imágenes

Ver [Issues](https://github.com/thecocoblue/file-converter-service/issues) para sugerir funcionalidades.

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Lee [CONTRIBUTING.md](CONTRIBUTING.md)
2. Fork el proyecto
3. Crea una rama (`git checkout -b feature/AmazingFeature`)
4. Commit tus cambios (`git commit -m 'feat: Add AmazingFeature'`)
5. Push a la rama (`git push origin feature/AmazingFeature`)
6. Abre un Pull Request

### Áreas donde puedes ayudar

- 🐛 Reportar bugs
- 📝 Mejorar documentación
- 🌐 Traducir a otros idiomas
- 💻 Agregar nuevas funcionalidades
- 🧪 Escribir tests
- ⭐ Dar estrella al repo

---

## 📝 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo de versiones.

### Versión 1.0.0 (Actual)

- ✅ Conversión de documentos, imágenes, audio y video
- ✅ API REST completa
- ✅ Conversión desde URL
- ✅ Health monitoring con métricas
- ✅ Logging estructurado
- ✅ Compresión GZIP
- ✅ Limpieza automática de archivos
- ✅ Docker y Docker Compose
- ✅ Documentación completa en español

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**thecocoblue**

- GitHub: [@thecocoblue](https://github.com/thecocoblue)
- Email: [luis.islas@ludaisca.com](mailto:luis.islas@ludaisca.com)

---

## 🙏 Agradecimientos

- [LibreOffice](https://www.libreoffice.org/) - Conversión de documentos
- [FFmpeg](https://ffmpeg.org/) - Procesamiento multimedia
- [ImageMagick](https://imagemagick.org/) - Procesamiento de imágenes
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Docker](https://www.docker.com/) - Containerización
- La comunidad de código abierto

---

## 🌟 Soporte

Si este proyecto te resulta útil:

- ⭐ Dale una estrella en GitHub
- 🐛 [Reporta bugs](https://github.com/thecocoblue/file-converter-service/issues)
- 💡 [Sugiere mejoras](https://github.com/thecocoblue/file-converter-service/issues/new)
- 🔀 Comparte con otros desarrolladores

---

**Última actualización**: 23 de diciembre de 2024 | **Versión**: 1.0.0
