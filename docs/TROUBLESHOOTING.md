# Guía de Solución de Problemas

Soluciones a problemas comunes del Servicio de Conversión de Archivos.

---

## Tabla de Contenidos

- [Problemas de Inicio](#problemas-de-inicio)
- [Errores de Conversión](#errores-de-conversión)
- [Problemas de Rendimiento](#problemas-de-rendimiento)
- [Errores de Red](#errores-de-red)
- [Problemas de Almacenamiento](#problemas-de-almacenamiento)
- [Errores Comunes de API](#errores-comunes-de-api)
- [Problemas de Docker](#problemas-de-docker)
- [FAQ](#faq)

---

## Problemas de Inicio

### El contenedor no inicia

**Síntoma**: `docker-compose up -d` falla o el contenedor se detiene inmediatamente.

**Diagnóstico**:
```bash
docker-compose logs file-converter
```

**Soluciones**:

1. **Puerto 5000 ya está en uso**
   ```bash
   # Verificar qué proceso usa el puerto
   sudo lsof -i :5000
   # o
   sudo netstat -tlnp | grep 5000
   
   # Cambiar el puerto en docker-compose.yml
   ports:
     - "5001:5000"  # Usar puerto 5001 en el host
   ```

2. **Permisos de volúmenes**
   ```bash
   # Verificar permisos
   ls -la ./uploads ./converted ./logs
   
   # Corregir permisos
   sudo chown -R $USER:$USER ./uploads ./converted ./logs
   chmod -R 755 ./uploads ./converted ./logs
   ```

3. **Memoria insuficiente**
   ```bash
   # Verificar memoria disponible
   free -h
   
   # Agregar límites en docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 512M
   ```

4. **Imagen corrupta**
   ```bash
   # Reconstruir desde cero
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up -d
   ```

---

## Errores de Conversión

### Error: "Conversion from .X to .Y is not supported"

**Causa**: Formato no soportado o combinación inválida.

**Solución**:
```bash
# Verificar formatos soportados
curl http://localhost:5000/formats | jq

# Ejemplo: .docx solo puede convertirse a .pdf, .txt, .html
# NO a .jpg (usa el conversor incorrecto)
```

### Error: "LibreOffice conversion failed"

**Síntoma**: Falla al convertir documentos de Office.

**Diagnóstico**:
```bash
# Verificar que LibreOffice esté instalado
docker exec -it file-converter-api which libreoffice
docker exec -it file-converter-api libreoffice --version
```

**Soluciones**:

1. **LibreOffice no responde**
   ```bash
   # Reiniciar el contenedor
   docker-compose restart file-converter
   ```

2. **Archivo corrupto**
   - Verifica que el archivo original se pueda abrir en LibreOffice localmente
   - Intenta con otro archivo del mismo tipo

3. **Timeout en archivos grandes**
   - Aumenta el timeout en tu proxy reverso (Nginx/Traefik)
   - Reduce el tamaño del archivo

### Error: "ImageMagick policy error"

**Síntoma**: Falla al convertir PDFs con ImageMagick.

**Solución**:
```bash
# Verificar política de ImageMagick
docker exec -it file-converter-api cat /etc/ImageMagick-6/policy.xml | grep PDF

# Debería mostrar: rights="read|write" pattern="PDF"
# Si no, reconstruir la imagen
docker-compose build --no-cache
```

### Error: "FFmpeg conversion failed"

**Síntoma**: Falla al convertir audio/video.

**Diagnóstico**:
```bash
# Verificar FFmpeg
docker exec -it file-converter-api ffmpeg -version

# Ver logs detallados
docker exec -it file-converter-api tail -f /app/logs/app.log
```

**Soluciones**:

1. **Códec no soportado**
   - Verifica que el archivo fuente sea válido
   - Intenta primero convertir con FFmpeg localmente

2. **Memoria insuficiente para video**
   - Aumenta el límite de memoria del contenedor
   - Reduce el tamaño del video

---

## Problemas de Rendimiento

### Conversiones muy lentas

**Causas posibles**:

1. **CPU limitada**
   ```bash
   # Verificar uso de CPU
   docker stats file-converter-api
   
   # Aumentar límite de CPU en docker-compose.yml
   deploy:
     resources:
       limits:
         cpus: '2.0'  # Aumentar de 1.0 a 2.0
   ```

2. **Disco lento (I/O)**
   ```bash
   # Verificar I/O
   iostat -x 1
   
   # Usar volumen en SSD si es posible
   # Evitar carpetas de red (NFS, SMB)
   ```

3. **Múltiples conversiones simultáneas**
   - El servicio procesa una conversión a la vez
   - Considera escalar horizontalmente (múltiples instancias)

### Alto uso de memoria

**Diagnóstico**:
```bash
# Monitorear memoria
docker stats file-converter-api

# Ver procesos dentro del contenedor
docker exec -it file-converter-api ps aux
```

**Soluciones**:

1. **Memory leak en proceso de conversión**
   ```bash
   # Reiniciar periódicamente (workaround)
   # Agregar a crontab:
   0 */6 * * * docker-compose restart file-converter
   ```

2. **Limpieza no funciona**
   ```bash
   # Verificar que el thread de limpieza esté corriendo
   docker exec -it file-converter-api ps aux | grep python
   
   # Limpiar manualmente
   docker exec -it file-converter-api find /app/uploads -type f -delete
   docker exec -it file-converter-api find /app/converted -type f -delete
   ```

---

## Errores de Red

### Error: "Connection refused" al hacer requests

**Soluciones**:

1. **Contenedor no está corriendo**
   ```bash
   docker-compose ps
   docker-compose up -d
   ```

2. **Firewall bloqueando el puerto**
   ```bash
   # Verificar firewall
   sudo ufw status
   
   # Permitir puerto 5000
   sudo ufw allow 5000/tcp
   ```

3. **Binding incorrecto**
   - Verifica que `app.py` use `host='0.0.0.0'` (no `127.0.0.1`)

### Error: "Download from URL failed"

**Síntoma**: No puede descargar archivos desde URLs.

**Diagnóstico**:
```bash
# Probar descarga desde el contenedor
docker exec -it file-converter-api curl -I https://ejemplo.com/archivo.pdf
```

**Soluciones**:

1. **URL inválida o inaccesible**
   - Verifica que la URL sea pública
   - Verifica que no requiera autenticación

2. **Timeout (archivos grandes)**
   - El timeout es de 30 segundos por defecto
   - Para archivos grandes, aumenta el timeout en `src/utils.py`

3. **Problemas de DNS**
   ```bash
   # Verificar DNS en el contenedor
   docker exec -it file-converter-api nslookup google.com
   
   # Agregar DNS en docker-compose.yml
   dns:
     - 8.8.8.8
     - 8.8.4.4
   ```

---

## Problemas de Almacenamiento

### Error: "Disk full" o "No space left on device"

**Diagnóstico**:
```bash
# Verificar espacio en disco
df -h

# Verificar tamaño de volúmenes
docker system df -v
```

**Soluciones**:

1. **Limpiar archivos viejos**
   ```bash
   # Limpieza manual
   docker exec -it file-converter-api find /app/uploads -type f -mtime +1 -delete
   docker exec -it file-converter-api find /app/converted -type f -mtime +1 -delete
   
   # Reducir FILE_TTL en .env
   FILE_TTL=1800  # 30 minutos en lugar de 1 hora
   ```

2. **Limpiar imágenes Docker no usadas**
   ```bash
   docker system prune -a
   docker volume prune
   ```

3. **Aumentar espacio en disco**
   - Expandir el volumen del servidor
   - Montar un volumen adicional para archivos

### Archivos no se limpian automáticamente

**Verificar**:
```bash
# Ver si el thread de limpieza está activo
docker logs file-converter-api | grep "cleanup"

# Verificar configuración
echo $CLEANUP_INTERVAL
echo $FILE_TTL
```

**Solución**:
```bash
# Reiniciar el servicio
docker-compose restart file-converter

# Verificar logs
docker logs -f file-converter-api
```

---

## Errores Comunes de API

### 400 Bad Request: "Target format not specified"

**Causa**: No se envió el parámetro `format`.

**Solución**:
```bash
# Incorrecto
curl -F "file=@documento.docx" http://localhost:5000/convert

# Correcto
curl -F "file=@documento.docx" -F "format=pdf" http://localhost:5000/convert
```

### 400 Bad Request: "Provide either file or url"

**Causa**: No se envió ni `file` ni `url`.

**Solución**:
```bash
# Enviar archivo
curl -F "file=@documento.docx" -F "format=pdf" http://localhost:5000/convert

# O enviar URL
curl -F "url=https://ejemplo.com/archivo.pdf" -F "format=jpg" http://localhost:5000/convert
```

### 413 Payload Too Large

**Causa**: Archivo excede `MAX_FILE_SIZE`.

**Solución**:

1. **Aumentar el límite** en `.env`:
   ```bash
   MAX_FILE_SIZE=100  # Aumentar a 100 MB
   ```

2. **Comprimir el archivo** antes de subirlo

3. **Configurar Nginx** para permitir archivos grandes:
   ```nginx
   client_max_body_size 100M;
   ```

### 404 Not Found: "File not found"

**Causas**:

1. **Archivo ya fue limpiado** (TTL expirado)
   - Descarga el archivo inmediatamente después de la conversión
   - Aumenta `FILE_TTL` en `.env`

2. **URL de descarga incorrecta**
   - Verifica que uses la URL completa de la respuesta
   - Ejemplo: `/download/abc123.pdf`

---

## Problemas de Docker

### "Cannot connect to Docker daemon"

**Solución**:
```bash
# Iniciar Docker
sudo systemctl start docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### "docker-compose: command not found"

**Solución**:
```bash
# Instalar Docker Compose
sudo apt update
sudo apt install docker-compose-plugin

# O usar docker compose (sin guión)
docker compose up -d
```

### Contenedor se reinicia constantemente

**Diagnóstico**:
```bash
# Ver estado
docker ps -a

# Ver logs de crash
docker logs file-converter-api
```

**Causas comunes**:
- Error en el código Python
- Puerto ya en uso
- Falta dependencia del sistema
- Configuración incorrecta en `.env`

---

## FAQ

### ¿Puedo convertir múltiples archivos simultáneamente?

No, el servicio procesa una conversión a la vez. Para múltiples conversiones simultáneas:
- Escala horizontalmente (múltiples instancias)
- Usa un balanceador de carga
- O procesa en cola (implementar sistema de colas)

### ¿Cuánto tiempo tardan las conversiones?

Depende del tipo y tamaño:
- Documentos: 2-10 segundos
- Imágenes: 1-5 segundos
- Audio: 5-30 segundos
- Video: 10 segundos - varios minutos

### ¿Puedo usar el servicio sin Docker?

Sí, sigue la [guía de despliegue manual](DEPLOYMENT.md#despliegue-manual).

### ¿Cómo aumento la seguridad?

1. Usa HTTPS siempre
2. Implementa autenticación (API key)
3. Configura rate limiting
4. Usa firewall
5. Mantente actualizado
6. Monitorea logs regularmente

### ¿Soporta autenticación?

No por defecto. Puedes:
- Agregar autenticación en el proxy reverso
- Implementar API keys en el código
- Usar VPN/red privada

### ¿Cómo integro con n8n?

Ver [ejemplos de integración en API.md](API.md#ejemplos-de-integración).

### ¿Puedo cambiar la calidad de conversión?

Actualmente no hay parámetros de calidad. La conversión usa configuración por defecto de cada herramienta.

Para personalizar:
- Modifica los conversores en `src/converters/`
- Agrega parámetros de calidad en la API

---

## Obtener Ayuda

Si tu problema no está aquí:

1. **Revisa los logs**:
   ```bash
   docker logs -f file-converter-api
   docker exec -it file-converter-api tail -f /app/logs/app.log
   ```

2. **Verifica el health check**:
   ```bash
   curl http://localhost:5000/health | jq
   ```

3. **Busca en GitHub Issues**:
   - [Issues existentes](https://github.com/thecocoblue/file-converter-service/issues)
   - [Crear nuevo issue](https://github.com/thecocoblue/file-converter-service/issues/new)

4. **Proporciona información**:
   - Versión de Docker: `docker --version`
   - Sistema operativo: `uname -a`
   - Logs completos
   - Comando que causa el error
   - Archivo `.env` (sin datos sensibles)

---

## Logs de Debug

Para habilitar logs detallados:

```bash
# En .env
LOG_LEVEL=DEBUG
FLASK_DEBUG=True  # Solo en desarrollo

# Reiniciar
docker-compose restart file-converter

# Ver logs en tiempo real
docker logs -f file-converter-api
```

**⚠️ Importante**: Desactiva `FLASK_DEBUG` en producción.
