# 🚀 Coolify Deployment Guide

## Problem: `no available server` Error

If you see `no available server` when accessing your application through Coolify:

```
curl -k https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/
no available server
```

This means:
- ✅ Coolify proxy is running
- ✅ Container is deployed
- ❌ Coolify cannot reach the container

---

## Solution: Coolify Configuration

### Step 1: Verify Container is Running

```bash
# SSH into your Orquestra host
ssh your-user@your-host

# Check Docker containers
docker ps | grep file-converter

# Should show something like:
# CONTAINER ID  IMAGE                              STATUS              PORTS
# abc123...     file-converter-service:latest      Up 5 minutes        5000/tcp
```

If container is NOT running:
```bash
# Check logs
docker logs <container-id>

# Restart container
docker restart <container-id>
```

### Step 2: Verify Container is Healthy

```bash
# Test from inside the container's network
docker exec <container-id> curl -f http://localhost:5000/health

# Should return JSON with 200 OK
# {"success": true, "status": "healthy", ...}
```

If this fails:
1. Check Flask is running: `docker logs <container-id>`
2. Verify port 5000 is open: `docker port <container-id>`
3. Restart: `docker restart <container-id>`

### Step 3: Configure Coolify Application Settings

In Coolify Dashboard:

1. Go to: **Applications** → **file-converter-service**

2. Find: **Networking** or **Ports** section

3. Set these values:
   ```
   Container Port: 5000
   Published Port: (leave empty - Coolify handles this)
   Protocol: HTTP (not HTTPS - Coolify adds HTTPS)
   Host: 0.0.0.0 (container should listen on all interfaces)
   ```

4. If there's a "Port Mapping" or "Expose Ports" section:
   - Enable port 5000
   - Make sure it's NOT trying to map to HTTPS

5. If there's a "Health Check" option:
   ```
   Path: /health
   Interval: 30s
   Timeout: 10s
   Retries: 3
   ```

### Step 4: Check Coolify Reverse Proxy

Coolify uses a reverse proxy (Nginx/Caddy). Verify it's configured:

```bash
# SSH into host and check if reverse proxy container exists
docker ps | grep coolify

# Should see something like:
# - coolify-proxy or nginx or caddy container running
# - Listening on port 80 and 443
```

### Step 5: Test Container Directly

If Coolify proxy still doesn't work, test container directly:

```bash
# From your local machine (if you have SSH access)
ssh user@orquestra-host

# Test locally on the host
curl http://localhost:5000/
curl http://localhost:5000/health

# Should return JSON with 200 OK
```

If this works but Coolify doesn't:
- Problem is in Coolify routing/proxy configuration
- Continue to Step 6

### Step 6: Fix Coolify Proxy Configuration

#### Option A: Redeploy Application

In Coolify Dashboard:

1. Go to **file-converter-service**
2. Click **Redeploy**
3. Wait 5-10 minutes for:
   - Container restart
   - Healthcheck to pass
   - Proxy to route correctly

#### Option B: Edit Docker Compose

If Coolify doesn't have the right compose file:

1. In Coolify Dashboard → **file-converter-service** → **Source**
2. Make sure it's using one of:
   - `docker-compose.yml` (development)
   - `docker-compose.production.yml` (production - recommended)

3. If using `docker-compose.production.yml`:
   - Container name: `file-converter-api`
   - Port: `5000:5000`
   - Health check enabled

#### Option C: Manual Coolify Configuration

If Coolify has a custom configuration file, ensure it has:

```yaml
services:
  file-converter-api:
    image: ludaisca/file-converter-service:latest
    container_name: file-converter-api
    restart: unless-stopped
    
    # CRITICAL: Port mapping
    ports:
      - "5000:5000"  # This is essential for Coolify
    
    # CRITICAL: Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Step 7: Verify Coolify Proxy Routing

```bash
# SSH into host
ssh user@orquestra-host

# Check if Coolify proxy container is running
docker ps | grep -E 'coolify|nginx|caddy'

# Check Coolify proxy logs
docker logs <proxy-container-id>

# Look for errors about "no available server" or routing issues
```

If you see routing errors:
1. The application container might not be healthy
2. The proxy configuration might be incorrect
3. The health check might be failing

### Step 8: Debug Network Connectivity

```bash
# SSH into host
ssh user@orquestra-host

# Check if container is reachable from proxy
docker exec <proxy-container-id> curl -f http://file-converter-api:5000/

# Or if container name is different
docker exec <proxy-container-id> curl -f http://localhost:5000/

# Should return JSON with 200 OK
```

If this fails:
- Containers are not on same network
- Container name doesn't match proxy configuration
- Application is crashing

---

## Common Issues and Solutions

### Issue 1: "no available server"

**Cause:** Proxy can't reach the application container

**Solutions:**
1. Verify container is running: `docker ps`
2. Verify health check passes: `docker exec <id> curl -f http://localhost:5000/health`
3. Redeploy in Coolify
4. Check Coolify proxy logs for routing errors
5. Verify port mapping: `docker port <container-id>` should show `5000/tcp`

### Issue 2: "SSL certificate problem"

**Cause:** Let's Encrypt certificate is still being generated

**Solution:**
```bash
# Temporary fix (5-10 min)
curl -k https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/

# Permanent: Wait for certificate to generate
# Usually takes 5-10 minutes from first deployment
```

### Issue 3: "TLS connect error: wrong version number"

**Cause:** Trying to send TLS/HTTPS to a port that only serves HTTP

**Solution:**
```bash
# DON'T do this:
curl -k https://dominio:5000/  # ❌ Wrong

# DO this:
curl -k https://dominio/      # ✅ Correct
```

### Issue 4: Container keeps restarting

**Cause:** Application crash or configuration error

**Solution:**
```bash
# Check logs
docker logs <container-id> --tail 50

# Look for:
# - Python errors
# - Missing dependencies
# - Port binding issues
# - Configuration errors

# Common fixes:
# 1. Rebuild image: docker-compose build --no-cache
# 2. Check requirements.txt: pip check
# 3. Verify app.py: python app.py
```

### Issue 5: Health check fails

**Cause:** Application not responding or endpoint doesn't exist

**Solution:**
```bash
# Test health check directly
docker exec <container-id> curl -v http://localhost:5000/health

# Should return:
# HTTP/1.1 200 OK
# {"success": true, "status": "healthy", ...}

# If it fails:
# 1. Check Flask is running: docker logs <container-id>
# 2. Verify /health endpoint exists in routes.py
# 3. Check application can start: docker run -it <image> /bin/bash
```

---

## Quick Troubleshooting Checklist

- [ ] Container is running: `docker ps | grep file-converter`
- [ ] Container is healthy: `docker exec <id> curl -f http://localhost:5000/health`
- [ ] Port is mapped: `docker port <container-id>` shows `5000/tcp`
- [ ] Coolify proxy is running: `docker ps | grep -E 'coolify|nginx|caddy'`
- [ ] Proxy can reach app: `docker exec <proxy-id> curl -f http://file-converter-api:5000/`
- [ ] Redeployed recently: Yes (Coolify Dashboard → Redeploy)
- [ ] Waited for certificate: Yes (5-10 minutes)
- [ ] Using correct URL format: `https://dominio/` (no `:5000`)

---

## Testing After Fix

```bash
# Test root endpoint
curl -k https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/

# Test health check
curl -k https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/health

# Test formats endpoint
curl -k https://e0kkgos0wok8kgo0o4gcksc8.orquestra.xyz/formats

# All should return JSON with 200 OK ✅
```

---

## Production Checklist

Before considering deployment complete:

- [ ] Application responds to all endpoints
- [ ] Health check passes
- [ ] SSL certificate is valid (no self-signed errors)
- [ ] Logs are properly configured (check `/app/logs`)
- [ ] Volume mounts are working (check `/app/uploads`, `/app/converted`)
- [ ] Restart policy is set to `unless-stopped`
- [ ] Resource limits are configured (if needed)
- [ ] Monitoring is set up (if applicable)
- [ ] Backup of volumes is scheduled (if applicable)

---

## Need More Help?

Check:
1. Coolify documentation: https://coolify.io/
2. Docker documentation: https://docs.docker.com/
3. Application logs: `docker logs <container-id> --tail 100 -f`
4. GitHub issues: https://github.com/ludaisca/file-converter-service/issues
