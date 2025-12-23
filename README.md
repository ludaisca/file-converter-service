# File Converter Microservice

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen)
![License MIT](https://img.shields.io/badge/License-MIT-yellow)

## Descripción Ejecutiva

Este proyecto es un microservicio API REST agnóstico diseñado para la orquestación robusta de conversiones de archivos multimedia. Actúa como una capa de abstracción sobre potentes herramientas de procesamiento como **FFmpeg** (audio/video), **LibreOffice** (documentos/headless), **ImageMagick** (imágenes) y **Tesseract OCR** (extracción de texto), proporcionando una interfaz unificada y segura para aplicaciones cliente.

La arquitectura está pensada para entornos de alta demanda, soportando despliegues contenerizados y pipelines de automatización.

## Capacidades Técnicas

### Matriz de Conversión (Soportada en v2.0.0)

El sistema utiliza un **Factory Pattern** para delegar la conversión al motor más adecuado:

| Categoría | Formatos de Entrada | Formatos de Salida | Motor |
|-----------|---------------------|--------------------|-------|
| **Documentos** | `.docx`, `.doc`, `.odt`, `.rtf`, `.txt`, `.html`, `.xlsx`, `.xls`, `.csv`, `.ods`, `.pptx`, `.ppt`, `.odp` | `.pdf`, `.docx`, `.doc`, `.txt`, `.html`, `.odt`, `.rtf`, `.xlsx`, `.xls`, `.csv`, `.ods`, `.pptx`, `.ppt`, `.odp` | LibreOffice |
| **Imágenes** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`, `.heic`, `.avif`, `.ico`, `.psd`, `.xcf` | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tiff`, `.ico`, `.pdf`, `.svg` | ImageMagick |
| **Audio/Video** | `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`, `.webm`, `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`, `.aac`, `.opus`, `.wma` | `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.gif`, `.webp`, `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`, `.aac`, `.opus`, `.wma` | FFmpeg |
| **Archivos** | `.zip`, `.7z`, `.rar`, `.tar`, `.gz`, `.bz2`, `.xz` | `.zip`, `.7z`, `.tar`, `.tar.gz` | Built-in (7z/tar) |

> **Nota:** El soporte de Audio y Video está activo y verificado en la versión actual.

### OCR (Reconocimiento Óptico de Caracteres)
El endpoint `/extract-text` permite extraer texto plano de documentos PDF escaneados e imágenes utilizando **Tesseract OCR**. Soporta preprocesamiento de imágenes para mejorar la precisión y configuración de idioma.

### Seguridad y Arquitectura
*   **Validación Estricta:** Uso de `magic numbers` para detección real de tipos MIME y listas blancas de extensiones.
*   **Sanitización:** Los nombres de archivo se limpian (`secure_filename`) y se anonimizan con UUIDs para prevenir colisiones y ataques de path traversal.
*   **Rate Limiting:** Protección contra abuso basada en IP o API Key.
*   **Configuración:** Gestión de entorno centralizada con **Pydantic**, asegurando tipado fuerte y validación de variables (e.g., `MAX_FILE_SIZE`).

## Guía de Instalación y Despliegue

### Requisitos Previos
*   Docker y Docker Compose

### Despliegue Rápido (Recomendado)

```bash
docker-compose up -d --build
```

El servicio estará disponible en `http://localhost:5000`.

### Variables de Entorno

La configuración se gestiona en `src/config.py`. Las principales variables son:

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `ENV` | Entorno de ejecución (`development`, `production`) | `development` |
| `PORT` | Puerto del servicio | `5000` |
| `MAX_FILE_SIZE` | Tamaño máximo de archivo (en bytes) | `524288000` (500MB) |
| `ENABLE_OCR` | Habilitar/Deshabilitar motor OCR | `True` |
| `OCR_DEFAULT_LANGUAGE` | Idioma por defecto para OCR | `spa` |
| `RATE_LIMIT_ENABLED` | Habilitar limitación de tasa | `True` |
| `WORKERS` | Número de workers (Gunicorn) | `4` |

## Documentación de la API

### 1. Verificar Estado
**GET** `/health`
Retorna métricas de salud del sistema (CPU, RAM, Espacio en disco) y estado de dependencias.

### 2. Convertir Archivo
**POST** `/convert`
Soporta carga directa de archivos o descarga desde URL.

**Parámetros (Multipart/Form-data):**
*   `file`: (Opcional) Archivo binario a convertir.
*   `url`: (Opcional) URL pública del archivo a procesar.
*   `format`: Extensión de destino (ej: `pdf`, `mp3`).

**Respuesta:**
```json
{
  "success": true,
  "file_id": "uuid...",
  "download_url": "/download/uuid.pdf",
  "output_size_mb": 1.2
}
```

### 3. Extraer Texto (OCR)
**POST** `/extract-text`
Extrae texto de imágenes o PDFs.

**Parámetros:**
*   `file` o `url`.
*   `lang`: Código de idioma (ej: `spa`, `eng`).
*   `preprocess`: `true`/`false` (mejorar imagen antes de OCR).

### 4. Descargar Archivo
**GET** `/download/<filename>`
Recupera el archivo convertido.

## Integraciones

Este microservicio es totalmente compatible con herramientas de automatización Low-Code como **n8n**. Puede integrarse fácilmente en flujos de trabajo para procesamiento masivo de documentos, conversión de medios o pipelines de ingestión de datos (ETL).

## Stack Tecnológico

*   **Core:** Python 3.11, Flask
*   **Servidor:** Gunicorn (Producción)
*   **Testing:** Pytest
*   **Colas/Caché:** Redis (Opcional, configurado para caché y rate limiting)
*   **Validación:** Pydantic
*   **Motores:** FFmpeg, LibreOffice, ImageMagick, Tesseract, 7zip, Poppler
