# Docker Best Practices for Orchestratorr

This document outlines best practices for building, deploying, and managing Orchestratorr containers.

## Image Building

### 1. Multi-Stage Builds

Both Dockerfiles use multi-stage builds to minimize image size:

**Benefits**:
- Reduces final image size by excluding build tools
- Faster pulls and deployments
- Smaller attack surface
- Lower storage costs

**Example**:
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime (only what's needed)
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
```

### 2. Minimize Layer Count

```dockerfile
# ❌ Bad: 3 layers
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get clean

# ✅ Good: 1 layer
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
```

### 3. Cache Leverage

Order Dockerfile commands from least to most frequently changed:

```dockerfile
# ✅ Good: stable layers first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then changing code
COPY . .
```

### 4. Use .dockerignore

Both projects include `.dockerignore` files that exclude:
- Version control (.git)
- Environment files (.env)
- Node modules / Python cache
- IDE settings
- OS files (Thumbs.db, .DS_Store)
- Docker files (prevents recursion)

**Result**: Smaller build context, faster builds

## Container Configuration

### 1. Non-Root User

**Why**: Security best practice; limits damage if container is compromised

Both Dockerfiles create a non-root user:

```dockerfile
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

**Verify**:
```bash
docker-compose exec backend whoami
# appuser
```

### 2. Health Checks

All services include health checks for orchestration:

**Backend**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

**Frontend**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/
```

**Check status**:
```bash
docker-compose ps
# Shows (healthy), (unhealthy), or (starting)
```

### 3. Environment Variables

Use `.env` file for configuration (already excluded by `.dockerignore`):

```bash
# .env
RADARR_URL=http://radarr:7878
RADARR_API_KEY=secret-key
LOG_LEVEL=INFO
```

**Load in compose**:
```yaml
env_file:
  - .env
```

**Never**:
- Hardcode secrets in Dockerfile
- Store credentials in images
- Commit .env files to git

### 4. Restart Policies

```yaml
restart: unless-stopped
```

**Options**:
- `no` - Don't restart
- `always` - Always restart if stopped/crashed
- `unless-stopped` - Always restart unless explicitly stopped
- `on-failure` - Restart only on non-zero exit code

### 5. Resource Limits

For production, add resource constraints:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

## Networking

### 1. Bridge Networks

Docker Compose creates a bridge network automatically:

```yaml
networks:
  orchestratorr-net:
    driver: bridge
```

**Benefits**:
- Containers can reach each other by service name
- Isolated from host network
- DNS resolution built-in

### 2. Service Discovery

Within Docker network, use service names as hostnames:

```bash
# From backend, reach frontend:
curl http://frontend

# From frontend (nginx), reach backend:
proxy_pass http://backend:8000;
```

### 3. Port Publishing

Only expose ports that are actually needed:

```yaml
services:
  backend:
    ports:
      - "8000:8000"  # Expose API
    # ❌ Don't expose internal ports

  frontend:
    ports:
      - "80:80"      # Expose web
      # ❌ Don't expose Nginx internals
```

## Production Deployments

### 1. Use Compose v2+ Format

Current setup uses `version: '3.8'` which is well-supported:

```yaml
version: '3.8'
# Supports:
# - Depends on with health checks
# - Named volumes
# - Custom networks
```

### 2. Environment-Specific Compose Files

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml up -d
```

**Production overrides**:
- Disable hot reload
- Increase resource limits
- Add backup volumes
- Configure logging drivers

### 3. Secret Management

**Don't use .env for secrets in production**. Instead:

```yaml
secrets:
  radarr_api_key:
    external: true  # Created separately

services:
  backend:
    secrets:
      - radarr_api_key
    environment:
      - RADARR_API_KEY_FILE=/run/secrets/radarr_api_key
```

**Create secrets**:
```bash
echo "your-secret-key" | docker secret create radarr_api_key -
```

### 4. Logging Configuration

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Alternatives**:
- `splunk` - Splunk Enterprise
- `awslogs` - CloudWatch
- `gcplogs` - Google Cloud Logging
- `awsfirelens` - ECS FireLens

### 5. Reverse Proxy (Traefik example)

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  frontend:
    image: orchestratorr-frontend
    labels:
      - "traefik.http.routers.frontend.rule=Host(`orchestratorr.example.com`)"
      - "traefik.http.services.frontend.loadbalancer.server.port=80"
```

## Optimization

### 1. Image Size

**Check image sizes**:
```bash
docker image ls | grep orchestratorr
```

**Optimize**:
- Use alpine base images (Linux 5-10 MB vs 50+ MB)
- Remove package managers after install (backend already does this)
- Multi-stage builds (both Dockerfiles use this)

### 2. Build Speed

**Improve cache hits**:
```bash
# Leverage cache
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Pull latest base images
docker-compose build --pull
```

### 3. Layer Caching

Order matters! Each unchanged layer can be cached:

```dockerfile
# ✅ Frequently cached
COPY requirements.txt .
RUN pip install -r requirements.txt

# ❌ Less frequently cached (rebuilds on any code change)
COPY . .
```

## Troubleshooting

### 1. Image Not Rebuilding

**Problem**: Changes don't appear after edits

**Solution**:
```bash
# Force rebuild
docker-compose build --no-cache

# Remove old images
docker image prune -a

# Restart
docker-compose up -d --build
```

### 2. Permission Denied Errors

**Problem**: `Permission denied: /app/file`

**Cause**: Container running as wrong user or missing permissions

**Solution**:
```bash
# Check running user
docker-compose exec backend whoami

# Check file permissions
docker-compose exec backend ls -la /app

# Rebuild with correct user
docker-compose build --no-cache
```

### 3. Out of Disk Space

**Problem**: `No space left on device`

**Solution**:
```bash
# Clean unused images
docker image prune -a

# Clean unused volumes
docker volume prune

# Clean build cache
docker builder prune -a

# Check disk usage
docker system df
```

### 4. Networking Issues

**Problem**: `Cannot reach backend from frontend`

**Debug**:
```bash
# Check running services
docker-compose ps

# Test connectivity from frontend
docker-compose exec frontend ping backend

# Check network
docker network ls
docker network inspect orchestratorr_orchestratorr-net

# Check logs
docker-compose logs frontend | grep error
```

## Security Checklist

- [ ] Non-root user in all Dockerfiles
- [ ] No hardcoded secrets
- [ ] .dockerignore excludes sensitive files
- [ ] Base images from official registries
- [ ] Scan images: `docker scan orchestratorr-backend`
- [ ] Pin base image versions (don't use `latest`)
- [ ] Update base images regularly
- [ ] Use secrets for API keys in production
- [ ] Enable health checks
- [ ] Limit resource usage
- [ ] Restrict network access
- [ ] Use read-only root filesystem (if possible)

## Performance Checklist

- [ ] Multi-stage builds to minimize image size
- [ ] Layer caching optimized
- [ ] Alpine base images (if applicable)
- [ ] Resource limits configured
- [ ] Health checks responsive
- [ ] Logging drivers configured
- [ ] Network optimized (service discovery via names)
- [ ] No unnecessary volumes mounted

## See Also

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Docker Compose Best Practices](https://docs.docker.com/compose/production/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
