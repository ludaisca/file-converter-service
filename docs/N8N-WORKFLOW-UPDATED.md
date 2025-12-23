# N8N Workflow - File Converter v2.1.0

## 🎉 AHORA CON SOPORTE COMPLETO DE AUDIO!

Tu workflow de Google Drive → Conversion ahora funciona con **68+ formatos** sin restricciones.

## ✨ Lo que cambió

**ANTES:**
- ❌ Audio NO funcionaba (ogg, mp3, wav error)
- ❌ 16 formatos soportados
- ❌ Error: "Unsupported format: ogg"

**AHORA:**
- ✅ Audio FUNCIONA (9 formatos!)
- ✅ 68+ formatos soportados
- ✅ SIN restricciones de conversión

## 📋 Configuración del Workflow

### Paso 1: Descarga desde Google Drive
```
Nodo: "Search files and folders1"
Carpeta: 251222
Retorna: Lista de archivos
```

### Paso 2: Descargar archivo
```
Nodo: "Download file"
Input: ID del archivo
Output: Contenido binario
```

### Paso 3: Determinar formato
```
Nodo: "Debug: Ver estructura"
Verifica: Tipo de archivo
Retorna: Información útil
```

### Paso 4: CONVERTIR (LA MAGIA)
```
Nodo: "HTTP Request (CAMBIAR FORMATO AQUÍ)"
Endpoint: https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/convert
Método: POST
Parámetros:
  - format: "ogg" ← EDITA ESTO
  - file: Contenido binario del archivo
```

## 🎯 Cambiar el formato de conversión

En el nodo **"HTTP Request (CAMBIAR FORMATO AQUÍ)"**, modificar:

```
"format": "ogg"  ← Cambiar a lo que necesites
```

### Ejemplos:

**Para audio:**
```
"format": "mp3"   // MP3
"format": "wav"   // WAV
"format": "ogg"   // OGG Vorbis
"format": "m4a"   // MPEG-4 Audio
"format": "flac"  // FLAC Lossless
"format": "aac"   // AAC
"format": "opus"  // Opus
"format": "wma"   // Windows Media Audio
```

**Para video:**
```
"format": "mp4"   // MP4
"format": "avi"   // AVI
"format": "mov"   // MOV (QuickTime)
"format": "mkv"   // Matroska
"format": "webm"  // WebM
"format": "gif"   // GIF (video → animación)
"format": "3gp"   // 3GP Mobile
```

**Para imagen:**
```
"format": "jpg"   // JPEG
"format": "png"   // PNG
"format": "gif"   // GIF
"format": "bmp"   // BMP
"format": "webp"  // WebP
"format": "tiff"  // TIFF
"format": "ico"   // ICO
"format": "pdf"   // PDF
```

**Para documento:**
```
"format": "pdf"   // PDF
"format": "docx"  // Word
"format": "doc"   // Word 97-2003
"format": "txt"   // Texto plano
"format": "html"  // HTML
"format": "csv"   // CSV
"format": "json"  // JSON
"format": "xml"   // XML
```

**Para archivos:**
```
"format": "zip"   // ZIP
"format": "7z"    // 7Z
"format": "tar"   // TAR
"format": "gz"    // GZIP
```

## 🚀 Uso del Workflow

### Opción 1: Interfaz N8N
1. Abre el workflow
2. Click en "Execute Workflow"
3. El workflow:
   - Descarga archivos desde Google Drive (carpeta 251222)
   - Los convierte al formato especificado
   - Retorna el resultado

### Opción 2: API Trigger (Webhook)
```bash
curl -X POST \
  https://[tu-n8n-instance]/webhook/file-converter \
  -H "Content-Type: application/json" \
  -d '{"folder": "251222", "format": "ogg"}'
```

### Opción 3: Ejecutar por Schedule
Configura un trigger cron para ejecutar automáticamente cada día/hora.

## 📊 Respuesta del Workflow

Cuando se ejecuta exitosamente:

```json
{
  "success": true,
  "file_id": "a7b3c9d2e1f4",
  "source_format": ".m4a",
  "output_format": "ogg",
  "output_size_mb": 4.5,
  "download_url": "/download/a7b3c9d2e1f4.ogg",
  "timestamp": "2025-12-23T20:56:00Z"
}
```

## ⚠️ Nota Importante

Después de deployar en Coolify (~20-30 minutos):

1. **Verifica que funciona:**
   ```bash
   curl https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/formats
   ```

2. **Ejecuta el workflow:**
   - Click en "Execute Workflow"
   - Espera a que descargue y convierta

3. **Si falla:**
   - Verifica el log del workflow en N8N
   - Confirma que el servicio esté deployado
   - Prueba con: `curl https://[dominio]/health`

## 💡 Tips

- **Batch processing:** Descomenta el nodo "Loop Over Items" para procesar múltiples archivos
- **Guardar en Drive:** Agrega un nodo "Google Drive Upload" después de la conversión
- **Notificaciones:** Agrega un nodo "Send Email" para notificar cuando termine

## 📚 Documentación Completa

- Ver: `COMPREHENSIVE_FORMATS_v2.1.0.md`
- GitHub: `/docs/SUPPORTED_FORMATS.md`
- API Docs: `curl /formats` (cuando esté deployado)

## 🤝 Soporte

¿Necesitas:
- Agregar más formatos?
- Cambiar la carpeta de Google Drive?
- Agregar procesamiento adicional?
- Guardar automáticamente en Drive?

¡Déjame saber!
