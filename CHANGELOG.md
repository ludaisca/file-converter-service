# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Planeado
- Autenticación con API Keys
- Rate limiting incorporado
- Sistema de cola con Redis
- Webhooks para notificaciones
- Conversión batch de múltiples archivos
- OCR para PDFs escaneados
- Watermarking de imágenes
- Compresión automática de archivos convertidos

## [1.0.0] - 2025-12-23

### Añadido
- Sistema de logging estructurado con rotación automática
- Health check endpoint con métricas del sistema (CPU, memoria, disco)
- Compresión Gzip automática de respuestas
- Soporte para conversión desde URL remota
- Documentación completa de API (API.md)
- Guía de despliegue en producción (DEPLOYMENT.md)
- Configuración de ejemplo (.env.example)
- Health check en Docker Compose
- Volúmen persistente para logs
- Sistema de limpieza automática de archivos temporales
- Validación de tamaño de archivos configurable
- Nombres de archivo seguros con UUID

### Conversiones Soportadas
- **Documentos**: DOCX, DOC, ODT, RTF → PDF, HTML, TXT
- **Imágenes**: JPG, PNG, GIF, BMP → JPG, PNG, PDF, WebP
- **Video**: MP4, AVI, MOV, MKV → MP4, AVI, GIF
- **Audio**: MP3, WAV, OGG, M4A, FLAC → MP3, WAV, OGG

### Dependencias
- Flask para API REST
- LibreOffice para conversión de documentos
- ImageMagick para procesamiento de imágenes
- FFmpeg para conversión multimedia
- Pandoc para conversiones avanzadas de documentos
- psutil para monitoreo de sistema

### Seguridad
- Sanitización de nombres de archivo
- Validación de extensiones permitidas
- Sin ejecución de código arbitrario
- Logs sin datos sensibles

## [0.3.0] - 2025-12-20

### Añadido
- Soporte para conversión de video a GIF
- Mejoras en el manejo de errores
- Tests automatizados para conversores

### Corregido
- Error al convertir archivos con nombres especiales
- Fuga de memoria en conversiones grandes

## [0.2.0] - 2025-12-15

### Añadido
- Conversión de archivos de audio
- Endpoint `/formats` para consultar formatos soportados
- Docker Compose para despliegue fácil

### Cambiado
- Estructura de proyecto reorganizada con patrón factory
- Mejoras en la velocidad de conversión de imágenes

## [0.1.0] - 2025-12-10

### Añadido
- Versión inicial del proyecto
- Conversión de documentos (DOCX → PDF)
- Conversión de imágenes (JPG, PNG)
- API REST básica con Flask
- Dockerfile para contenerización
- README.md con documentación básica

---

## Leyenda de Tipos de Cambios

- **Añadido**: Para nuevas funcionalidades
- **Cambiado**: Para cambios en funcionalidades existentes
- **Deprecado**: Para funcionalidades que serán eliminadas pronto
- **Eliminado**: Para funcionalidades eliminadas
- **Corregido**: Para corrección de bugs
- **Seguridad**: En caso de vulnerabilidades

---

## Enlaces

- [Repositorio](https://github.com/thecocoblue/file-converter-service)
- [Issues](https://github.com/thecocoblue/file-converter-service/issues)
- [Documentación API](./API.md)
- [Guía de Despliegue](./DEPLOYMENT.md)