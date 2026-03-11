# Docker Setup for Orchestratorr

This directory contains Docker configuration files for running Orchestratorr in containerized environments.

## Overview

Orchestratorr is configured to run both frontend and backend services using Docker and Docker Compose:

- **Backend**: FastAPI application running on port 8000
- **Frontend**: SvelteKit application served via Nginx on port 80
- **Network**: Private Docker network for inter-service communication

## Files

- `docker-compose.yml` - Main composition at project root (not in this folder)
- `../backend/Dockerfile` - Backend container configuration
- `../frontend/Dockerfile` - Frontend container configuration
- `../backend/.dockerignore` - Excludes unnecessary files from backend image
- `../frontend/.dockerignore` - Excludes unnecessary files from frontend image

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd orchestratorr
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your Radarr/Sonarr/Lidarr/Prowlarr API keys and URLs:

```env
RADARR_URL=http://your-radarr-host:7878
RADARR_API_KEY=your-api-key
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

### 3. Build and Run

```bash
# Build both images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Frontend**: http://localhost (or http://your-server-ip)
- **Backend API**: http://localhost:8000/docs (Swagger UI)
- **Backend Health**: http://localhost:8000/health

## Service Details

### Backend Service

**Container Name**: `orchestratorr-backend`

**Port Mapping**: `8000:8000`

**Environment Variables**:
- `FASTAPI_HOST=0.0.0.0` - Listen on all interfaces
- `FASTAPI_PORT=8000` - API port
- `FASTAPI_RELOAD=false` - Disable hot reload in production
- `LOG_LEVEL=INFO` - Logging level
- `RADARR_URL` - Radarr service URL (from .env)
- `RADARR_API_KEY` - Radarr API key (from .env)

**Health Check**: Python HTTP request to `/health` endpoint

**Network**: `orchestratorr-net` (bridge)

**Startup Policy**: `unless-stopped` (auto-restart on failure)

### Frontend Service

**Container Name**: `orchestratorr-frontend`

**Port Mapping**: `80:80`

**Build Arguments**:
- `VITE_API_BASE=""` - Use relative paths; Nginx proxies `/api` to backend

**Dependencies**: Waits for backend to be healthy before starting

**Health Check**: HTTP HEAD request to root path

**Network**: `orchestratorr-net` (bridge)

**Nginx Configuration**:
- Gzip compression enabled
- Security headers configured
- SPA routing with `/index.html` fallback
- `/api/*` requests proxied to backend container

## Docker Compose Commands

```bash
# Start services in background
docker-compose up -d

# View running services
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View frontend logs only
docker-compose logs -f frontend

# Stop all services (don't remove)
docker-compose stop

# Restart services
docker-compose restart

# Remove all containers (keeps images)
docker-compose down

# Remove containers, networks, and images
docker-compose down -v --rmi all

# Execute command in running container
docker-compose exec backend python -m pytest

# Rebuild images
docker-compose build --no-cache
```

## Advanced Usage

### Custom Port Mapping

Edit `docker-compose.yml` to change port bindings:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Backend on 8001
  
  frontend:
    ports:
      - "3000:80"    # Frontend on 3000
```

### Persistent Data Volumes

Add volumes to preserve data or configuration:

```yaml
volumes:
  backend_config:
    driver: local

services:
  backend:
    volumes:
      - backend_config:/app/config
```

### Environment Override

Create `.env.docker` for Docker-specific settings:

```bash
RADARR_URL=http://radarr:7878  # Use service name in Docker network
FASTAPI_RELOAD=false
```

Load it with: `docker-compose --env-file .env.docker up`

### Multi-Stage Builds

Both Dockerfiles use multi-stage builds to optimize image size:

**Backend**:
- Stage 1: `python:3.11-slim` with build tools → compile dependencies
- Stage 2: `python:3.11-slim` minimal → copy compiled packages

**Frontend**:
- Stage 1: `node:20-alpine` → build SvelteKit app
- Stage 2: `nginx:alpine` → serve static files

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep -E "FASTAPI|RADARR"

# Test API connectivity
docker-compose exec backend curl -s http://localhost:8000/health
```

### Frontend shows 502 Bad Gateway

**Issue**: Nginx can't reach backend

**Solution**:
```bash
# Check backend is running
docker-compose ps

# Verify network connectivity
docker-compose exec frontend ping backend

# Check Nginx config
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### Changes not reflected

**Issue**: Using old Docker images

**Solution**:
```bash
# Rebuild images with fresh layers
docker-compose build --no-cache

# Remove old images
docker image prune -a

# Rebuild and restart
docker-compose up -d --build
```

### Port already in use

**Issue**: Port 80 or 8000 is occupied

**Solution**:
```bash
# Find process using port
lsof -i :80
lsof -i :8000

# Kill process
kill -9 <PID>

# OR use different ports in docker-compose.yml
```

## Production Considerations

### Security

- [ ] Set environment variables securely (not in .env file)
- [ ] Use Docker secrets for sensitive data
- [ ] Enable HTTPS with reverse proxy (nginx, Traefik)
- [ ] Restrict network access with firewall rules
- [ ] Run containers as non-root (already configured)
- [ ] Scan images for vulnerabilities: `docker scan orchestratorr-backend`

### Performance

- [ ] Enable layer caching: `docker-compose build --no-cache`
- [ ] Monitor resource usage: `docker stats`
- [ ] Add resource limits:

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

### Logging

- [ ] Configure log rotation to prevent disk fill
- [ ] Use centralized logging (ELK stack, Loki)
- [ ] Monitor health checks: `docker-compose logs --since 30m backend`

### Updates

```bash
# Pull latest base images
docker-compose pull

# Rebuild application images
docker-compose build --pull

# Restart services
docker-compose up -d
```

## Networking

### Internal Communication

- Backend: `http://backend:8000` (from other containers)
- Frontend: `http://frontend` (from other containers)

### External Access

- Frontend: `http://localhost` or `http://<server-ip>`
- Backend API docs: `http://localhost:8000/docs`

### Network Isolation

Containers run on private `orchestratorr-net` bridge network. They cannot access external services unless:
1. Service is exposed on `0.0.0.0` (default)
2. Port is published with `ports:`
3. External service is reachable from container's network

## Development vs Production

### Development

```bash
# Mount local source for hot reload
docker-compose -f docker-compose.dev.yml up

# Rebuild on code changes
docker-compose build --no-cache
```

### Production

```bash
# Use environment variables securely
docker-compose --env-file /secure/path/.env.prod up -d

# Pin specific image versions in docker-compose.yml
# Rebuild frequently to get security updates
docker-compose build --pull --no-cache
```

## See Also

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [SvelteKit Deployment Guide](https://kit.svelte.dev/docs/building-your-app)
- [Nginx Documentation](https://nginx.org/en/docs/)
