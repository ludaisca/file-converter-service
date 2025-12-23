# File Converter Microservice

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Descripción Ejecutiva

Este proyecto implementa una **API REST agnóstica** diseñada para la orquestación y conversión de archivos multimedia a gran escala. Actúa como un middleware unificado que abstrae la complejidad de múltiples herramientas de procesamiento de bajo nivel.

El servicio integra tecnologías líderes en la industria como **FFmpeg** para procesamiento audiovisual, **LibreOffice** (en modo headless) para documentos ofimáticos, **ImageMagick** para manipulación de imágenes y **Tesseract OCR** para la extracción de texto. Su arquitectura basada en microservicios y contenedorización con Docker facilita su despliegue en cualquier infraestructura, desde entornos locales hasta clusters de Kubernetes.

## Capacidades Técnicas

### Matriz de Conversión

El núcleo del sistema utiliza un **Factory Pattern** (`src/converters/factory.py`) para enrutar dinámicamente las solicitudes a los convertidores especializados.

| Categoría | Formatos de Entrada (Origen) | Formatos de Salida (Destino) | Motor |
| :--- | :--- | :--- | :--- |
| **Documentos** | `.docx`, `.doc`, `.odt`, `.rtf`, `.txt`, `.pdf`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.csv`, `.json`, `.xml` | `.pdf`, `.docx`, `.doc`, `.txt`, `.html`, `.odt`, `.rtf`, `.csv`, `.json`, `.xml` | LibreOffice |
| **Hojas de Cálculo** | `.xlsx`, `.xls`, `.csv`, `.ods` | `.xlsx`, `.xls`, `.csv`, `.pdf`, `.json`, `.xml` | LibreOffice |
| **Presentaciones** | `.pptx`, `.ppt`, `.odp` | `.pptx`, `.ppt`, `.pdf`, `.html` | LibreOffice |
| **Imágenes** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif`, `.webp`, `.svg`, `.heic`, `.avif`, `.ico`, `.psd`, `.xcf` | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tiff`, `.ico`, `.pdf`, `.svg` | ImageMagick |
| **Audio** | `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`, `.aac`, `.opus`, `.wma`, `.aiff`, `.ape` | `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`, `.aac`, `.opus`, `.wma`, `.aiff` | FFmpeg |
| **Video** | `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`, `.webm`, `.m4v`, `.3gp`, `.f4v`, `.m2ts` | `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`, `.gif`, `.webp`, `.3gp` | FFmpeg |
| **Archivos** | `.zip`, `.7z`, `.rar`, `.tar`, `.gz`, `.bz2`, `.xz` | `.zip`, `.7z`, `.tar`, `.tar.gz` | Archive Utils |
| **Web** | `.html`, `.htm`, `.css`, `.js` | `.html`, `.htm`, `.pdf` | LibreOffice |

### OCR (Reconocimiento Óptico de Caracteres)

El servicio expone capacidades de OCR mediante el endpoint `/extract-text`. Utiliza **Tesseract OCR** para procesar imágenes y documentos PDF, permitiendo la extracción de texto plano para indexación o análisis.

### Seguridad y Arquitectura

*   **Validación Estricta**: Implementada en `src/validators.py` y `src/config.py` usando **Pydantic**. Se validan extensiones, tipos MIME y tamaños de archivo antes del procesamiento.
*   **Sanitización**: Todos los nombres de archivo son sanitizados (`secure_filename`) y se les asigna un **UUID** único para prevenir colisiones y ataques de path traversal.
*   **Autenticación**: Soporte para **API Key** (`src/auth.py`), permitiendo asegurar los endpoints en entornos de producción.
*   **Factory Pattern**: Desacopla la lógica de recepción de la lógica de conversión, permitiendo agregar nuevos formatos sin modificar el núcleo de la aplicación.

## Guía de Instalación y Despliegue

### Despliegue con Docker (Recomendado)

Para levantar el servicio en un entorno aislado y listo para producción:

```bash
docker-compose up -d --build
```

El servicio estará disponible en `http://localhost:5000`.

### Variables de Entorno

La configuración se gestiona mediante variables de entorno, validadas estrictamente por Pydantic al inicio.

| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `ENV` | Entorno de ejecución (`development`, `production`, `testing`) | `development` |
| `PORT` | Puerto de escucha del servicio | `5000` |
| `MAX_FILE_SIZE` | Tamaño máximo de archivo permitido (en bytes) | `524288000` (500MB) |
| `UPLOAD_FOLDER` | Directorio temporal para subidas | `/tmp/file-converter/uploads` |
| `CONVERTED_FOLDER` | Directorio para archivos procesados | `/tmp/file-converter/converted` |
| `ENABLE_OCR` | Habilitar/Deshabilitar motor OCR | `True` |
| `OCR_DEFAULT_LANGUAGE` | Idioma por defecto para OCR (ISO 639-2) | `spa` |
| `API_KEY` | Clave para autenticación (si se requiere) | - |

## Documentación de la API

### Endpoints Principales

#### `GET /health`
Verifica el estado del servicio y métricas del sistema.
*   **Respuesta**: Estado `healthy`, uso de CPU/RAM, disponibilidad de disco.

#### `POST /convert`
Realiza la conversión de un archivo.
*   **Body (Multipart)**: `file` (binario).
*   **Body (Form)**: `url` (para descarga remota), `format` (extensión destino, ej: `pdf`).
*   **Respuesta**: JSON con ID de archivo y URL de descarga.

#### `POST /extract-text`
Extrae texto de un archivo (Imagen/PDF).
*   **Body**: `file` o `url`.
*   **Parámetros**: `lang` (opcional, ej: `eng`), `preprocess` (bool).
*   **Respuesta**: JSON con el texto extraído y nivel de confianza.

#### `GET /download/<filename>`
Recupera el archivo procesado.
*   **Parámetros**: Nombre del archivo retornado por `/convert`.

## Integraciones

Este microservicio está diseñado para integrarse nativamente con herramientas de orquestación de flujos de trabajo como **n8n**, **Zapier** o **Airflow**. Su arquitectura stateless y respuestas JSON estandarizadas lo hacen ideal para pipelines de procesamiento de documentos automatizados.

## Stack Tecnológico

*   **Framework Web**: Flask
*   **Servidor WSGI**: Gunicorn (recomendado para producción)
*   **Validación**: Pydantic
*   **Testing**: Pytest
*   **Procesamiento**:
    *   FFmpeg
    *   LibreOffice
    *   ImageMagick
    *   Tesseract
    *   7zip / Tar

---
**Versión 2.0.0**
*Refactorización completa con manejo robusto de excepciones y configuración validada.*
