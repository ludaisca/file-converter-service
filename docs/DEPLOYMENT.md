# Guía de Despliegue

Guía completa para desplegar el Servicio de Conversión de Archivos en diferentes entornos.

---

## Tabla de Contenidos

- [Despliegue con Docker Compose](#despliegue-con-docker-compose)
- [Despliegue en Coolify](#despliegue-en-coolify)
- [Despliegue Manual](#despliegue-manual)
- [Variables de Entorno](#variables-de-entorno)
- [Configuración de Proxy Reverso](#configuración-de-proxy-reverso)
- [Monitoreo y Logs](#monitoreo-y-logs)
- [Backup y Mantenimiento](#backup-y-mantenimiento)

---

## Despliegue con Docker Compose

### Requisitos
- Docker 20.10+
- Docker Compose 2.0+
- 512 MB RAM mínimo (1 GB recomendado)
- 2 GB espacio en disco

### Pasos

1. **Clonar el repositorio**
```bash
git clone https://github.com/thecocoblue/file-converter-service.git
cd file-converter-service
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
nano .env  # Ajusta los valores según tus necesidades
```

3. **Iniciar el servicio**
```bash
docker-compose up -d
```

4. **Verificar que está corriendo**
```bash
docker-compose ps
curl http://localhost:5000/health
```

5. **Ver logs**
```bash
docker-compose logs -f file-converter
```

### Detener el servicio
```bash
docker-compose down
```

### Actualizar el servicio
```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Despliegue en Coolify

### Opción 1: Despliegue desde GitHub (Recomendado)

1. **En Coolify, crear nuevo recurso**
   - Ve a tu proyecto en Coolify
   - Click en "+ New Resource"
   - Selecciona "Docker Compose"

2. **Configurar el repositorio**
   - Repository URL: `https://github.com/thecocoblue/file-converter-service.git`
   - Branch: `main`
   - Build Pack: `nixpacks` o `dockerfile`

3. **Configurar variables de entorno**
   
   En la sección "Environment Variables":
   ```bash
   FLASK_ENV=production
   MAX_FILE_SIZE=50
   MAX_DOWNLOAD_SIZE=100
   CLEANUP_INTERVAL=3600
   FILE_TTL=3600
   LOG_LEVEL=INFO
   ```

4. **Configurar dominio**
   - En "Domains", agrega tu dominio: `converter.tudominio.com`
   - Coolify configurará SSL automáticamente con Let's Encrypt

5. **Configurar almacenamiento persistente**
   
   En "Persistent Storage", agregar:
   ```
   /app/uploads -> uploads
   /app/converted -> converted
   /app/logs -> logs
   ```

6. **Configurar Health Check**
   - Health Check Path: `/health`
   - Health Check Port: `5000`
   - Health Check Interval: `30s`

7. **Desplegar**
   - Click en "Deploy"
   - Espera a que el build termine
   - Verifica en `https://converter.tudominio.com/health`

### Opción 2: Despliegue con Docker Compose en Coolify

1. **Crear nuevo Docker Compose Service**
   - En Coolify: "+ New Resource" → "Docker Compose"

2. **Pegar el docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     file-converter:
       image: ghcr.io/thecocoblue/file-converter-service:latest
       container_name: file-converter-api
       ports:
         - "5000:5000"
       volumes:
         - uploads:/app/uploads
         - converted:/app/converted
         - logs:/app/logs
       environment:
         - FLASK_ENV=production
         - MAX_FILE_SIZE=50
         - MAX_DOWNLOAD_SIZE=100
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
         interval: 30s
         timeout: 5s
         retries: 3
         start_period: 10s
   
   volumes:
     uploads:
     converted:
     logs:
   ```

3. **Configurar y desplegar**

### Configuración Avanzada en Coolify

#### Resource Limits
En la configuración del contenedor:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

#### Logging
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## Despliegue Manual

### En un servidor Ubuntu/Debian

1. **Instalar dependencias del sistema**
```bash
sudo apt update
sudo apt install -y \
  python3.11 \
  python3-pip \
  libreoffice \
  imagemagick \
  ffmpeg \
  pandoc \
  ghostscript \
  poppler-utils
```

2. **Clonar y configurar**
```bash
git clone https://github.com/thecocoblue/file-converter-service.git
cd file-converter-service
pip3 install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
nano .env
```

4. **Crear directorios**
```bash
mkdir -p /app/uploads /app/converted /app/logs
```

5. **Ejecutar con systemd**

Crear `/etc/systemd/system/file-converter.service`:
```ini
[Unit]
Description=File Converter Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/file-converter-service
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/opt/file-converter-service/.env
ExecStart=/usr/bin/python3 /opt/file-converter-service/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Iniciar el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable file-converter
sudo systemctl start file-converter
sudo systemctl status file-converter
```

---

## Variables de Entorno

### Variables Requeridas

Ninguna variable es estrictamente requerida (todas tienen defaults), pero se recomienda configurar:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Entorno de Flask |
| `MAX_FILE_SIZE` | `50` | Tamaño máximo de subida en MB |
| `MAX_DOWNLOAD_SIZE` | `100` | Tamaño máximo de descarga en MB |

### Variables Opcionales

| Variable | Default | Descripción |
|----------|---------|-------------|
| `FLASK_DEBUG` | `False` | Modo debug (solo desarrollo) |
| `UPLOAD_FOLDER` | `/app/uploads` | Directorio de subidas |
| `CONVERTED_FOLDER` | `/app/converted` | Directorio de archivos convertidos |
| `LOGS_FOLDER` | `/app/logs` | Directorio de logs |
| `CLEANUP_INTERVAL` | `3600` | Intervalo de limpieza en segundos |
| `FILE_TTL` | `3600` | Tiempo de vida de archivos en segundos |
| `LOG_LEVEL` | `INFO` | Nivel de logging (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | `/app/logs/app.log` | Ruta del archivo de log |
| `ENABLE_HEALTH_MONITORING` | `True` | Habilitar monitoreo de salud |
| `API_VERSION` | `1.0.0` | Versión de la API |

### Ejemplo de .env para Producción

```bash
# Flask
FLASK_ENV=production
FLASK_DEBUG=False

# Límites de archivos
MAX_FILE_SIZE=100        # 100 MB para archivos grandes
MAX_DOWNLOAD_SIZE=200    # 200 MB para descargas

# Limpieza agresiva (cada 30 minutos, TTL de 1 hora)
CLEANUP_INTERVAL=1800
FILE_TTL=3600

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/app/logs/app.log

# Monitoreo
ENABLE_HEALTH_MONITORING=True

# API
API_VERSION=1.0.0
```

---

## Configuración de Proxy Reverso

### Nginx

Crear `/etc/nginx/sites-available/file-converter`:

```nginx
server {
    listen 80;
    server_name converter.tudominio.com;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name converter.tudominio.com;

    # SSL (Certbot configurará esto)
    ssl_certificate /etc/letsencrypt/live/converter.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/converter.tudominio.com/privkey.pem;

    # Tamaño máximo de subida
    client_max_body_size 100M;

    # Timeouts para conversiones largas
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    send_timeout 300;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Logging
    access_log /var/log/nginx/file-converter-access.log;
    error_log /var/log/nginx/file-converter-error.log;
}
```

Activar:
```bash
sudo ln -s /etc/nginx/sites-available/file-converter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Traefik (Docker)

En `docker-compose.yml`:

```yaml
services:
  file-converter:
    # ... configuración existente ...
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.file-converter.rule=Host(`converter.tudominio.com`)"
      - "traefik.http.routers.file-converter.entrypoints=websecure"
      - "traefik.http.routers.file-converter.tls.certresolver=letsencrypt"
      - "traefik.http.services.file-converter.loadbalancer.server.port=5000"
    networks:
      - traefik-network

networks:
  traefik-network:
    external: true
```

---

## Monitoreo y Logs

### Verificar Salud
```bash
curl https://converter.tudominio.com/health | jq
```

### Ver Logs en Docker
```bash
# Logs en tiempo real
docker-compose logs -f file-converter

# Últimas 100 líneas
docker-compose logs --tail=100 file-converter

# Logs desde hace 1 hora
docker-compose logs --since 1h file-converter
```

### Ver Logs en Coolify
- Ve a tu servicio en Coolify
- Click en "Logs"
- Puedes filtrar por fecha/hora

### Logs persistentes
Los logs se guardan en `/app/logs/app.log` dentro del contenedor (mapeado al volumen `logs`).

### Configurar rotación de logs

Crear `/etc/logrotate.d/file-converter`:
```
/var/lib/docker/volumes/file-converter_logs/_data/app.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

---

## Backup y Mantenimiento

### Backup de Volúmenes

```bash
# Backup de archivos convertidos
docker run --rm \
  -v file-converter_converted:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/converted-$(date +%Y%m%d).tar.gz /data

# Backup de logs
docker run --rm \
  -v file-converter_logs:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/logs-$(date +%Y%m%d).tar.gz /data
```

### Restaurar Backup

```bash
docker run --rm \
  -v file-converter_converted:/data \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/converted-20241223.tar.gz -C /
```

### Limpieza Manual

```bash
# Entrar al contenedor
docker exec -it file-converter-api /bin/bash

# Limpiar archivos viejos manualmente
find /app/uploads -type f -mtime +1 -delete
find /app/converted -type f -mtime +1 -delete
```

### Actualización del Servicio

```bash
# 1. Hacer backup
./backup.sh

# 2. Actualizar código
git pull origin main

# 3. Reconstruir imagen
docker-compose build --no-cache

# 4. Reiniciar servicio
docker-compose down
docker-compose up -d

# 5. Verificar
curl http://localhost:5000/health
```

---

## Troubleshooting

### El servicio no inicia

1. Verificar logs:
```bash
docker-compose logs file-converter
```

2. Verificar puertos:
```bash
sudo netstat -tlnp | grep 5000
```

3. Verificar permisos de volúmenes:
```bash
docker exec -it file-converter-api ls -la /app
```

### Conversiones fallan

1. Verificar que las herramientas estén instaladas:
```bash
docker exec -it file-converter-api which libreoffice
docker exec -it file-converter-api which convert  # ImageMagick
docker exec -it file-converter-api which ffmpeg
```

2. Verificar logs de error:
```bash
docker exec -it file-converter-api tail -f /app/logs/app.log
```

### Disco lleno

1. Verificar espacio:
```bash
df -h
```

2. Limpiar archivos viejos:
```bash
docker exec -it file-converter-api find /app/uploads -type f -delete
docker exec -it file-converter-api find /app/converted -type f -delete
```

3. Reducir `FILE_TTL` en `.env`

---

## Seguridad en Producción

### Recomendaciones

1. **Usar HTTPS siempre** (Coolify lo hace automáticamente)
2. **Configurar firewall**:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

3. **Limitar tamaño de archivos** en `.env`
4. **Configurar rate limiting** en Nginx/Traefik
5. **Monitorear uso de recursos** regularmente
6. **Mantener Docker actualizado**

---

## Soporte

Para más ayuda:
- 🐛 [Reportar un bug](https://github.com/thecocoblue/file-converter-service/issues)
- 📚 [Ver documentación completa](https://github.com/thecocoblue/file-converter-service)
- 💬 [Discusiones](https://github.com/thecocoblue/file-converter-service/discussions)
