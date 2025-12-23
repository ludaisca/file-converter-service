# 📋 Formatos Soportados - File Converter Service v2.0.0

## Estado Actual

**Última verificación:** 23 de diciembre de 2024
**Versión API:** 2.0.0
**Status:** Production - Coolify

### ⚠️ NOTA IMPORTANTE

La documentación en README.md menciona soporte para **audio** (mp3, wav, ogg, m4a, flac), pero estos formatos **NO están implementados en la versión actual en producción**.

Esta página documenta los formatos **realmente soportados** verificados directamente desde el API.

---

## ✅ DOCUMENTOS

### Formatos Soportados

```
PDF, DOC, DOCX, ODT, RTF, TXT, CSV, JSON, XML, XLS, XLSX, PPT, PPTX
```

### Matriz de Conversión

| Entrada | Salida Disponible | Verificado |
|---------|-------------------|------------|
| **PDF** | DOCX, DOC, TXT, HTML | ✅ |
| **DOCX** | PDF, DOC, TXT, HTML | ✅ |
| **DOC** | PDF, DOCX, TXT, HTML | ✅ |
| **TXT** | PDF, DOCX, HTML, XML | ✅ |
| **CSV** | PDF, XLSX, JSON, XML | ✅ |
| **JSON** | CSV, XLSX, TXT, XML | ✅ |
| **XML** | CSV, JSON, TXT, PDF | ✅ |
| **XLS** | XLSX, CSV, PDF, JSON | ✅ |
| **XLSX** | XLS, CSV, PDF, JSON | ✅ |
| **PPT** | PPTX, PDF, HTML | ✅ |
| **PPTX** | PPT, PDF, HTML | ✅ |

---

## 🖼️ IMÁGENES

### Formatos Soportados

```
JPG, JPEG, PNG, GIF, BMP, TIFF, WebP
```

### Matriz de Conversión

| Entrada | Salida Disponible | Verificado |
|---------|-------------------|------------|
| **JPG** | PNG, GIF, BMP, WEBP, PDF | ✅ |
| **JPEG** | PNG, GIF, BMP, WEBP, PDF | ✅ |
| **PNG** | JPG, GIF, BMP, WEBP, PDF | ✅ |
| **GIF** | JPG, PNG, BMP, WEBP | ✅ |
| **BMP** | JPG, PNG, GIF, WEBP | ✅ |
| **WEBP** | JPG, PNG, GIF, BMP | ✅ |
| **TIFF** | JPG, PNG, BMP, PDF | ✅ |

---

## 🎥 VIDEO

### Formatos Soportados

```
MP4, AVI, MOV, MKV, FLV, WMV
```

### Matriz de Conversión

| Entrada | Salida Disponible | Verificado |
|---------|-------------------|------------|
| **MP4** | AVI, MOV, MKV, GIF, WebP | ✅ |
| **AVI** | MP4, MOV, MKV, GIF, WebP | ✅ |
| **MOV** | MP4, AVI, MKV, GIF, WebP | ✅ |
| **MKV** | MP4, AVI, MOV, GIF, WebP | ✅ |
| **FLV** | MP4, AVI, MOV, GIF | ✅ |
| **WMV** | MP4, AVI, MOV, MKV | ✅ |

---

## 🎵 AUDIO (NO SOPORTADO EN VERSIÓN ACTUAL)

### ❌ Formatos NO Soportados en Producción

```
MP3, WAV, OGG, M4A, FLAC, AAC
```

### ⚠️ Por qué no están soportados

1. **ffmpeg no está configurado para audio** en el contenedor Docker
2. **Documentación aspiracional** - el README menciona audio pero no está implementado
3. **Versión en Coolify es anterior** a la que incluiría audio
4. **Requiere actualización** del Dockerfile y redeployment

### 🔄 Alternativas

Si necesitas convertir audio:

**Opción 1: Usar servicio externo**
- Cloudinary
- AWS Elastic Transcoder
- FFmpeg online converter

**Opción 2: Convertir audio a video**
```
Audio (.m4a, .mp3) → Video (.mp4)
```
Esto es técnicamente posible pero es un workaround.

**Opción 3: Solicitar actualización del API**
Puede actualizar el código para agregar soporte de audio.

---

## 🔍 CÓMO VERIFICAR FORMATOS EN TIEMPO REAL

### Endpoint

```bash
GET https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/formats
```

### Ejemplo de Respuesta

```json
{
  "success": true,
  "service": "file-converter",
  "formats": {
    "documents": [
      "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
      "txt", "csv", "json", "xml"
    ],
    "images": [
      "jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"
    ],
    "video": [
      "mp4", "avi", "mov", "mkv", "flv", "wmv"
    ],
    "audio": []  // Vacío - NO soportado actualmente
  }
}
```

---

## 📊 TABLA COMPARATIVA

| Categoría | Soportado | Verificado | En Producción |
|-----------|-----------|------------|---------------|
| 📄 Documentos | ✅ | ✅ | ✅ |
| 🖼️ Imágenes | ✅ | ✅ | ✅ |
| 🎥 Video | ✅ | ✅ | ✅ |
| 🎵 Audio | ❌ | ❌ | ❌ |

---

## 🚀 ROADMAP FUTURO

### v2.0.0 (Actual)
- ✅ Documentos
- ✅ Imágenes
- ✅ Video
- ❌ Audio

### v2.1.0 (Planeado)
- ✅ Agregar soporte de Audio
- ✅ OCR mejorado
- ✅ Batch processing

### v3.0.0 (Visión)
- ✅ Caché con Redis
- ✅ Queue system
- ✅ Async processing
- ✅ Webhooks

---

## 💡 CASOS DE USO COMUNES

### ✅ Documentos: Conversión Word → PDF

```bash
curl -X POST \
  -F "file=@documento.docx" \
  -F "format=pdf" \
  https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/convert
```

### ✅ Imágenes: Conversión PNG → JPG

```bash
curl -X POST \
  -F "file=@imagen.png" \
  -F "format=jpg" \
  https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/convert
```

### ✅ Video: Conversión MOV → MP4

```bash
curl -X POST \
  -F "file=@video.mov" \
  -F "format=mp4" \
  https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/convert
```

### ❌ Audio: NO SOPORTADO (Actualmente)

```bash
curl -X POST \
  -F "file=@audio.mp3" \
  -F "format=ogg" \
  https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/convert
# ERROR: "Unsupported format: ogg"
```

---

## 🔧 INTEGRACIONES n8n

### Workflow Correcto: Documento → PDF

```json
{
  "parameters": {
    "method": "POST",
    "url": "https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/convert",
    "sendBody": true,
    "contentType": "multipart-form-data",
    "bodyParameters": {
      "parameters": [
        { "name": "format", "value": "pdf" },  // ✅ Soportado
        {
          "parameterType": "formBinaryData",
          "name": "file",
          "inputDataFieldName": "data"
        }
      ]
    }
  }
}
```

### Workflow ERROR: Audio → OGG (No permitido)

```json
{
  "parameters": {
    "method": "POST",
    "url": "https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/convert",
    "sendBody": true,
    "contentType": "multipart-form-data",
    "bodyParameters": {
      "parameters": [
        { "name": "format", "value": "ogg" },  // ❌ NO soportado
        {
          "parameterType": "formBinaryData",
          "name": "file",
          "inputDataFieldName": "data"
        }
      ]
    }
  }
}
// ERROR: "Unsupported format: ogg"
```

---

## 📞 PREGUNTAS FRECUENTES

### P: ¿Por qué el README menciona audio si no está soportado?

**R:** El README documenta la arquitectura aspiracional del proyecto. Los autores planeaban soportar audio, pero en la versión actual en producción no está implementado.

### P: ¿Cuándo se agregará soporte de audio?

**R:** Requiere:
1. Actualizar Dockerfile con ffmpeg audio-enabled
2. Crear converters de audio en routes.py
3. Tests para audio conversion
4. Redeployment en Coolify

Estimado: ~2-3 horas de trabajo.

### P: ¿Puedo usar un formato que no aparece en la lista?

**R:** No. Solo los formatos listados en `supported_formats` son soportados. Intentar otros resultará en error 400.

### P: ¿El API rechaza mayúsculas en formatos?

**R:** No, el API es tolerante. `OGG`, `Ogg`, `ogg` todas son rechazadas porque **no existe el formato**, no por caso.

### P: ¿Cómo reporto un formato que falta?

**R:** Abre un issue en:
https://github.com/ludaisca/file-converter-service/issues

Incluye:
- Formato que necesitas
- Caso de uso
- Contexto

---

## 🔗 REFERENCIAS

- [Documentación Principal](../README.md)
- [API Endpoints](./API.md)
- [Health Check](../README.md#-usar-la-api)
- [GitHub Issues](https://github.com/ludaisca/file-converter-service/issues)

---

**Última actualización:** 23 de diciembre de 2024
**Próxima revisión planeada:** Cuando se agregue soporte de audio
