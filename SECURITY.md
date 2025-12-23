# Política de Seguridad

## Versiones Soportadas

Actualmente se proporciona soporte de seguridad para las siguientes versiones:

| Versión | Soportada          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reportar una Vulnerabilidad

La seguridad del proyecto es una prioridad. Si descubres una vulnerabilidad de seguridad, te pedimos que nos la reportes de forma responsable.

### Cómo Reportar

**NO** abras un issue público para vulnerabilidades de seguridad.

En su lugar:

1. **Envía un correo a**: [luis.islas@ludaisca.com](mailto:luis.islas@ludaisca.com)
2. **Incluye**:
   - Descripción detallada de la vulnerabilidad
   - Pasos para reproducir el problema
   - Versión afectada
   - Impacto potencial
   - Solución propuesta (si la tienes)

3. **Respuesta esperada**:
   - Confirmación de recepción: 48 horas
   - Análisis inicial: 5 días hábiles
   - Actualización de estado: cada 7 días hasta resolución

### Proceso de Divulgación

1. Recibimos tu reporte
2. Confirmamos la vulnerabilidad
3. Desarrollamos un parche
4. Lanzamos una actualización de seguridad
5. Publicamos un aviso de seguridad
6. Te acreditamos en el aviso (si lo deseas)

---

## Medidas de Seguridad Implementadas

### Validación de Archivos

- **Sanitización de nombres**: Uso de `secure_filename()` de Werkzeug
- **Nombres únicos**: Generación de UUIDs para evitar colisiones
- **Validación de tamaño**: Límites configurables (`MAX_FILE_SIZE`, `MAX_DOWNLOAD_SIZE`)
- **Validación de extensión**: Solo formatos soportados son procesados

### Seguridad en Descargas

- **Timeout**: 30 segundos para descargas desde URL
- **Stream processing**: Descarga por chunks para evitar saturar memoria
- **Validación de tamaño**: Cancelación automática si excede límite
- **Limpieza automática**: Eliminación de archivos en caso de error

### Políticas de Conversión

#### ImageMagick
- **Política modificada**: PDF tiene permisos `read|write` controlados
- **Ubicación**: `/etc/ImageMagick-6/policy.xml`
- **Configuración**:
  ```xml
  <policy domain="coder" rights="read|write" pattern="PDF" />
  ```

### Gestión de Archivos Temporales

- **TTL configurable**: Archivos se eliminan después de `FILE_TTL` segundos
- **Limpieza automática**: Thread dedicado ejecuta limpieza cada `CLEANUP_INTERVAL`
- **Directorios aislados**: Separación entre uploads y convertidos

### Logging y Auditoría

- **Logs estructurados**: Registro de todas las operaciones
- **Sin datos sensibles**: Los logs no contienen contenido de archivos
- **Niveles configurables**: Control de verbosidad con `LOG_LEVEL`

---

## Recomendaciones de Seguridad para Producción

### 1. Red y Acceso

✅ **Usar HTTPS siempre**
```nginx
# Redirigir HTTP a HTTPS
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

✅ **Configurar firewall**
```bash
# Solo permitir puertos necesarios
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5000/tcp  # No exponer puerto directo
sudo ufw enable
```

✅ **Usar proxy reverso**
- Nginx, Traefik, o Caddy
- Nunca exponer el puerto 5000 directamente a internet

### 2. Autenticación y Autorización
⚠️ **El servicio NO incluye autenticación por defecto**

Implementa una de estas opciones:

**Opción A: API Key en Nginx**
```nginx
location / {
    if ($http_x_api_key != "tu-clave-secreta") {
        return 401;
    }
    proxy_pass http://localhost:5000;
}
```

**Opción B: Basic Auth en Nginx**
```nginx
location / {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:5000;
}
```

**Opción C: VPN/Red Privada**
- Usa Tailscale, WireGuard, o VPN corporativa
- Solo accesible desde red privada

### 3. Rate Limiting

✅ **Configurar límites de tasa en Nginx**
```nginx
http {
    limit_req_zone $binary_remote_addr zone=converter:10m rate=10r/m;
    
    server {
        location /convert {
            limit_req zone=converter burst=5;
            proxy_pass http://localhost:5000;
        }
    }
}
```

### 4. Límites de Recursos

✅ **Configurar límites en Docker**
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

✅ **Límites de tamaño de archivo**
```bash
# En .env
MAX_FILE_SIZE=50        # 50 MB
MAX_DOWNLOAD_SIZE=100   # 100 MB
```

✅ **Límites en Nginx**
```nginx
client_max_body_size 100M;
client_body_timeout 60s;
```

### 5. Aislamiento

✅ **Usar red Docker aislada**
```yaml
networks:
  converter-network:
    driver: bridge
    internal: true  # No acceso a internet si no es necesario
```

✅ **Ejecutar como usuario no-root**
```dockerfile
RUN useradd -m -u 1000 converter
USER converter
```

### 6. Actualizaciones

✅ **Mantener dependencias actualizadas**
```bash
# Actualizar imagen base
docker pull python:3.11-slim

# Reconstruir
docker-compose build --no-cache
```

✅ **Actualizar dependencias del sistema**
```dockerfile
RUN apt-get update && apt-get upgrade -y
```

### 7. Monitoreo

✅ **Monitorear logs regularmente**
```bash
# Buscar actividad sospechosa
grep -i "error\|fail\|attack" /var/log/nginx/access.log
```

✅ **Alertas de health check**
- Configura monitoreo (UptimeRobot, Healthchecks.io)
- Alertas si el servicio cae

✅ **Monitoreo de recursos**
```bash
# CPU, memoria, disco
docker stats file-converter-api
```

---

## Vulnerabilidades Conocidas

### Limitaciones Actuales

1. **Sin autenticación integrada**
   - **Impacto**: Cualquiera con acceso a la URL puede usar el servicio
   - **Mitigación**: Implementar autenticación en proxy reverso

2. **Sin rate limiting integrado**
   - **Impacto**: Posible abuso/DoS
   - **Mitigación**: Configurar rate limiting en Nginx/Traefik

3. **Sin validación de contenido de archivo**
   - **Impacto**: Archivos maliciosos podrían procesarse
   - **Mitigación**: Las herramientas de conversión están aisladas en contenedor

4. **Sin cifrado de archivos en reposo**
   - **Impacto**: Archivos almacenados en texto plano
   - **Mitigación**: Usar cifrado a nivel de volumen/disco

5. **Sin timeout en conversiones**
   - **Impacto**: Conversión larga puede saturar recursos
   - **Mitigación**: Configurar timeout en proxy reverso

---

## Checklist de Seguridad

Antes de desplegar en producción:

- [ ] HTTPS configurado con certificado válido
- [ ] Firewall activo y configurado
- [ ] Proxy reverso configurado (Nginx/Traefik)
- [ ] Autenticación implementada
- [ ] Rate limiting configurado
- [ ] Resource limits configurados en Docker
- [ ] Logs monitoreados
- [ ] Health checks configurados
- [ ] Backups automatizados
- [ ] Variables de entorno seguras (no hardcodeadas)
- [ ] Puerto 5000 NO expuesto directamente
- [ ] `FLASK_DEBUG=False` en producción
- [ ] Dependencias actualizadas
- [ ] Política de limpieza configurada (`FILE_TTL`)

---

## Buenas Prácticas de Uso

### Para Usuarios

1. **No subas archivos con información sensible**
   - Los archivos se almacenan temporalmente en el servidor
   - Usa cifrado antes de subir archivos confidenciales

2. **Descarga archivos rápidamente**
   - Los archivos se eliminan después del TTL
   - No confies en el almacenamiento a largo plazo

3. **Verifica el tamaño de tus archivos**
   - Respeta los límites de `MAX_FILE_SIZE`
   - Comprime archivos grandes antes de subir

### Para Administradores

1. **Revisa logs regularmente**
   ```bash
   tail -f /app/logs/app.log | grep -i "error\|fail"
   ```

2. **Monitorea uso de recursos**
   ```bash
   docker stats file-converter-api
   ```

3. **Actualiza regularmente**
   - Revisa releases: https://github.com/thecocoblue/file-converter-service/releases
   - Aplica parches de seguridad rápidamente

4. **Haz backups**
   - Aunque los archivos son temporales, haz backup de configuración
   - Documenta tu setup de deployment

---

## Recursos Adicionales

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Nginx Security](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [Flask Security](https://flask.palletsprojects.com/en/latest/security/)

---

## Contacto de Seguridad

**Email**: [luis.islas@ludaisca.com](mailto:luis.islas@ludaisca.com)

**PGP Key**: (Aún no configurado)

**Tiempo de Respuesta**: 48-72 horas

---

Última actualización: 23 de diciembre de 2024
