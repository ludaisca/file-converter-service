# 🚀 Guía de Despliegue

Guía completa para desplegar File Converter Service en producción.

## 📦 Requisitos de Producción
### Hardware Mínimo

- **CPU**: 2 cores
- **RAM**: 4GB (recomendado 8GB)
- **Almacenamiento**: 20GB SSD
- **Ancho de banda**: 100 Mbps

### Software

- Docker >= 20.10
- Docker Compose >= 2.0
- Nginx (para reverse proxy)
- Certbot (para SSL/TLS)

---

## 🐳 Despliegue con Docker Compose

### 1. Preparación del Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Añadir usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clonar Repositorio

```bash
# Crear directorio de aplicaciones
sudo mkdir -p /opt/services
cd /opt/services

# Clonar repositorio
git clone https://github.com/thecocoblue/file-converter-service.git
cd file-converter-service
```

### 3. Configuración de Entorno

```bash
# Copiar template de configuración
cp .env.example .env

# Editar configuración
nano .env
```

**Configuración de producción (.env):**

```env
# Entorno
FLASK_ENV=production

# Límites
MAX_FILE_SIZE=100

# Logging
LOG_LEVEL=INFO

# Puerto (interno del contenedor)
PORT=5000
```

### 4. Docker Compose para Producción

Crea `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  file-converter:
    build: .
    container_name: file-converter
    restart: unless-stopped
    
    environment:
      - FLASK_ENV=${FLASK_ENV:-production}
      - MAX_FILE_SIZE=${MAX_FILE_SIZE:-100}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    
    volumes:
      - ./uploads:/app/uploads
      - ./converted:/app/converted
      - ./logs:/app/logs
    
    networks:
      - converter-network
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 512M
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  converter-network:
    driver: bridge
```

### 5. Iniciar Servicio

```bash
# Construir imagen
docker-compose -f docker-compose.prod.yml build

# Iniciar servicio
docker-compose -f docker-compose.prod.yml up -d

# Verificar estado
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🌐 Configuración de Nginx como Reverse Proxy

### 1. Instalar Nginx

```bash
sudo apt install nginx -y
```

### 2. Configurar Virtual Host

Crea `/etc/nginx/sites-available/file-converter`:

```nginx
upstream file_converter {
    server localhost:5000;
}

server {
    listen 80;
    server_name converter.tudominio.com;

    # Aumentar límite de tamaño de archivo
    client_max_body_size 100M;
    client_body_timeout 300s;

    # Logs
    access_log /var/log/nginx/file-converter-access.log;
    error_log /var/log/nginx/file-converter-error.log;

    # Proxy headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # Timeouts para conversiones largas
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    location / {
        proxy_pass http://file_converter;
    }

    # Compresión gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
}
```

### 3. Habilitar Sitio

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/file-converter /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

### 4. Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot --nginx -d converter.tudominio.com

# Renovación automática (ya configurada)
sudo certbot renew --dry-run
```

**Configuración SSL final:**

```nginx
server {
    listen 443 ssl http2;
    server_name converter.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/converter.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/converter.tudominio.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... resto de configuración ...
}

server {
    listen 80;
    server_name converter.tudominio.com;
    return 301 https://$server_name$request_uri;
}
```

---

## ☁️ Despliegue en Coolify

### Opción 1: Docker Compose

1. **Crear nuevo recurso** en Coolify
2. **Seleccionar**: Docker Compose
3. **Repositorio**: `https://github.com/thecocoblue/file-converter-service.git`
4. **Branch**: `main`
5. **Docker Compose File**: `docker-compose.yml`

### Opción 2: Dockerfile

1. **Crear nuevo recurso** en Coolify
2. **Seleccionar**: Docker
3. **Repositorio**: `https://github.com/thecocoblue/file-converter-service.git`
4. **Branch**: `main`
5. **Build Pack**: Dockerfile

### Variables de Entorno en Coolify

Configura en el panel de Coolify:

```
FLASK_ENV=production
MAX_FILE_SIZE=100
LOG_LEVEL=INFO
```

### Configurar Dominio

1. En Coolify, ve a **Domains**
2. Agrega: `converter.tudominio.com`
3. Habilita **Auto SSL** (Let's Encrypt)

### Health Check en Coolify

- **Path**: `/health`
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3

---

## 📊 Monitoreo y Observabilidad

### 1. Prometheus + Grafana

Añade a `docker-compose.prod.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - converter-network

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - converter-network
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=changeme

volumes:
  prometheus-data:
  grafana-data:
```

**prometheus.yml:**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'file-converter'
    static_configs:
      - targets: ['file-converter:5000']
    metrics_path: '/health'
```

### 2. Logging Centralizado con Loki

```yaml
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    networks:
      - converter-network

  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./logs:/var/log/app
      - ./promtail-config.yml:/etc/promtail/config.yml
    networks:
      - converter-network

volumes:
  loki-data:
```

### 3. Uptime Monitoring

Usa servicios externos:

- **UptimeRobot**: https://uptimerobot.com
- **Pingdom**: https://www.pingdom.com
- **Better Uptime**: https://betteruptime.com

**Configuración:**
- URL: `https://converter.tudominio.com/health`
- Intervalo: 5 minutos
- Alert cuando: `status != "healthy"`

---

## 🛡️ Seguridad

### 1. Firewall (UFW)

```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilitar firewall
sudo ufw enable

# Verificar estado
sudo ufw status
```

### 2. Fail2Ban

```bash
# Instalar
sudo apt install fail2ban -y

# Configurar para Nginx
sudo nano /etc/fail2ban/jail.local
```

**jail.local:**

```ini
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/file-converter-error.log

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/file-converter-access.log
maxretry = 6
```

### 3. Rate Limiting en Nginx

Añade a la configuración de Nginx:

```nginx
http {
    # Zona de rate limiting
    limit_req_zone $binary_remote_addr zone=converter:10m rate=10r/s;
    
    server {
        # Aplicar rate limiting
        location /convert {
            limit_req zone=converter burst=20 nodelay;
            proxy_pass http://file_converter;
        }
    }
}
```

---

## 💾 Backup y Recuperación

### Script de Backup

Crea `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups/file-converter"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/services/file-converter-service"

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"

# Detener servicio
cd "$APP_DIR"
docker-compose -f docker-compose.prod.yml down

# Backup de volúmenes
tar -czf "$BACKUP_DIR/volumes_$DATE.tar.gz" uploads/ converted/ logs/

# Backup de configuración
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" .env docker-compose.prod.yml

# Reiniciar servicio
docker-compose -f docker-compose.prod.yml up -d

# Limpiar backups antiguos (mantener últimos 7 días)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Automatizar con Cron

```bash
# Editar crontab
crontab -e

# Backup diario a las 2 AM
0 2 * * * /opt/services/file-converter-service/backup.sh >> /var/log/backup.log 2>&1
```

### Restaurar desde Backup

```bash
#!/bin/bash

BACKUP_FILE="$1"
APP_DIR="/opt/services/file-converter-service"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file.tar.gz>"
    exit 1
fi

# Detener servicio
cd "$APP_DIR"
docker-compose -f docker-compose.prod.yml down

# Restaurar
tar -xzf "$BACKUP_FILE" -C "$APP_DIR"

# Reiniciar
docker-compose -f docker-compose.prod.yml up -d

echo "Restore completed"
```

---

## 🚀 Escalado Horizontal

### Load Balancer con Nginx

```nginx
upstream file_converter_cluster {
    least_conn;
    server converter1.local:5000;
    server converter2.local:5000;
    server converter3.local:5000;
}

server {
    listen 443 ssl http2;
    server_name converter.tudominio.com;

    location / {
        proxy_pass http://file_converter_cluster;
    }
}
```

### Docker Swarm

```bash
# Inicializar swarm
docker swarm init

# Crear servicio escalado
docker service create \
    --name file-converter \
    --replicas 3 \
    --publish 5000:5000 \
    --env FLASK_ENV=production \
    file-converter:latest

# Escalar
docker service scale file-converter=5
```

---

## 📝 Checklist de Despliegue

### Pre-Despliegue

- [ ] Servidor con requisitos mínimos
- [ ] Docker y Docker Compose instalados
- [ ] Dominio configurado (DNS apuntando al servidor)
- [ ] Certificado SSL configurado
- [ ] Firewall configurado
- [ ] Variables de entorno configuradas
- [ ] Backup configurado

### Post-Despliegue

- [ ] Servicio iniciado correctamente
- [ ] Health check retorna "healthy"
- [ ] SSL funcionando (https://)
- [ ] Logs generándose correctamente
- [ ] Monitoreo activo
- [ ] Backup automatizado funcionando
- [ ] Rate limiting probado
- [ ] Prueba de conversión exitosa

### Mantenimiento Semanal

- [ ] Revisar logs de errores
- [ ] Verificar espacio en disco
- [ ] Revisar métricas de uso
- [ ] Verificar backups
- [ ] Actualizar dependencias si es necesario

---

## 🎓 Mejores Prácticas

1. **Nunca expongas el puerto 5000 directamente** - Siempre usa Nginx como reverse proxy
2. **Habilita HTTPS siempre** - Usa Let's Encrypt gratuitamente
3. **Configura rate limiting** - Previene abuso del servicio
4. **Monitorea recursos** - CPU, RAM, disco pueden llenarse rápidamente
5. **Automatiza backups** - Pérdida de datos es inaceptable
6. **Usa logs rotativos** - Los logs pueden llenar el disco
7. **Implementa health checks** - Detecta problemas temprano
8. **Documenta cambios** - Mantén un changelog de despliegues

---

## ❓ Soporte

Si encuentras problemas durante el despliegue:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica el health check: `curl https://tudominio.com/health`
3. Consulta la documentación: [README.md](./README.md)
4. Reporta issues: https://github.com/thecocoblue/file-converter-service/issues