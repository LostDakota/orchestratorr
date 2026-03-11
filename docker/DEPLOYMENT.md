# Docker Deployment Guide

This guide covers deploying Orchestratorr in various environments using Docker.

## Deployment Targets

### 1. Local Development

**Use**: Single developer machine, learning, testing

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**Features**:
- Hot reload for code changes
- Full logging output
- Easy debugging
- Access on `http://localhost`

### 2. Home Server / NAS

**Use**: Home media server with existing *arr setup

```bash
# Copy project to server
git clone <repo> /opt/orchestratorr
cd /opt/orchestratorr
cp .env.example .env

# Edit .env with your *arr details
nano .env

# Start services
docker-compose up -d

# Monitor
docker-compose logs -f
```

**Configuration Example**:
```env
# Point to existing services (same network or accessible IPs)
RADARR_URL=http://192.168.1.100:7878
RADARR_API_KEY=your-api-key
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
LOG_LEVEL=INFO
```

### 3. VPS / Cloud Server

**Use**: Remote dedicated server (DigitalOcean, Linode, AWS, etc.)

#### Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker-compose --version
```

#### Setup
```bash
# Create app directory
mkdir -p /opt/apps/orchestratorr
cd /opt/apps/orchestratorr

# Clone repository
git clone <repo> .

# Configure
cp .env.example .env
nano .env  # Edit with your settings

# Start
docker-compose up -d

# Monitor
docker-compose logs -f
```

#### SSL/HTTPS Setup (Nginx Reverse Proxy)

Create `/opt/apps/nginx/docker-compose.yml`:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - reverse-proxy

networks:
  reverse-proxy:
    driver: bridge
```

Create `/opt/apps/nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name orchestratorr.example.com;
        return 301 https://$host$request_uri;
    }

    # HTTPS
    server {
        listen 443 ssl http2;
        server_name orchestratorr.example.com;
        
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        location / {
            proxy_pass http://frontend:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }
        
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }
    }
}
```

Get SSL certificate (Let's Encrypt):

```bash
# Using Certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --standalone -d orchestratorr.example.com

# Copy to nginx config directory
sudo cp /etc/letsencrypt/live/orchestratorr.example.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/orchestratorr.example.com/privkey.pem ./ssl/key.pem
```

### 4. Docker Swarm

**Use**: Multiple servers, high availability

```bash
# Initialize swarm (on manager node)
docker swarm init

# Create stack
docker stack deploy -c docker-compose.yml orchestratorr

# Monitor
docker service ls
docker service logs orchestratorr_backend
```

Update `docker-compose.yml` for swarm:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 512M
    networks:
      - orchestratorr-net

  frontend:
    build: ./frontend
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
    networks:
      - orchestratorr-net

networks:
  orchestratorr-net:
    driver: overlay
```

### 5. Kubernetes

**Use**: Container orchestration, enterprise deployments

Create `k8s/backend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orchestratorr-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: orchestratorr-backend
  template:
    metadata:
      labels:
        app: orchestratorr-backend
    spec:
      containers:
      - name: backend
        image: orchestratorr-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: FASTAPI_HOST
          value: "0.0.0.0"
        - name: FASTAPI_PORT
          value: "8000"
        - name: RADARR_URL
          valueFrom:
            configMapKeyRef:
              name: orchestratorr-config
              key: radarr_url
        - name: RADARR_API_KEY
          valueFrom:
            secretKeyRef:
              name: orchestratorr-secrets
              key: radarr_api_key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "500m"
            memory: "256Mi"
```

Create secrets:

```bash
kubectl create secret generic orchestratorr-secrets \
  --from-literal=radarr_api_key=your-api-key

kubectl create configmap orchestratorr-config \
  --from-literal=radarr_url=http://radarr:7878
```

Deploy:

```bash
kubectl apply -f k8s/
```

## Monitoring

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost/

# Full status
docker-compose ps
```

### Resource Monitoring

```bash
# Real-time stats
docker stats

# Inspect specific container
docker inspect orchestratorr-backend

# View detailed logs
docker-compose logs --timestamps backend
```

### Logging

Configure centralized logging:

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "orchestratorr"
    labels:
      - "orchestratorr.service=backend"
```

## Backup & Recovery

### Database/Config Backup

```bash
# Create backup
docker-compose exec -T backend python -c "import shutil; shutil.copytree('/app/config', '/tmp/backup')"
docker cp orchestratorr-backend:/tmp/backup ./backups/$(date +%Y%m%d)

# Restore
docker cp ./backups/20240101 orchestratorr-backend:/app/config
docker-compose restart backend
```

### Docker Volume Backup

```bash
# Backup volume
docker run --rm -v orchestratorr_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/volume-backup.tar.gz -C /data .

# Restore
docker run --rm -v orchestratorr_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/volume-backup.tar.gz -C /data
```

### Automated Backup with Cron

```bash
#!/bin/bash
# /usr/local/bin/backup-orchestratorr.sh

BACKUP_DIR=/backup/orchestratorr
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup docker volumes
docker run --rm \
  -v orchestratorr_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/orchestratorr-$DATE.tar.gz -C /data .

# Keep only last 7 days
find $BACKUP_DIR -name "orchestratorr-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/orchestratorr-$DATE.tar.gz"
```

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-orchestratorr.sh
```

## Updates & Maintenance

### Updating Application

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build --pull --no-cache

# Stop old version
docker-compose down

# Start new version
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Updating Base Images

```bash
# Check for updates
docker-compose pull

# Rebuild with latest base images
docker-compose build --pull

# Restart
docker-compose up -d
```

### Security Patches

```bash
# Scan for vulnerabilities
docker scan orchestratorr-backend
docker scan orchestratorr-frontend

# Update dependencies
# Backend
docker-compose exec backend pip install --upgrade -r requirements.txt

# Frontend
docker-compose exec frontend npm update
```

## Troubleshooting Deployments

### Services Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Validate compose file
docker-compose config --quiet

# Check port conflicts
netstat -tulpn | grep -E ':(80|8000)'

# Check disk space
df -h
```

### Performance Issues

```bash
# Monitor resource usage
docker stats

# Check for memory leaks
docker logs --since 1h backend | grep -i memory

# Adjust resource limits
# Edit docker-compose.yml and add:
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 512M
```

### Network Issues

```bash
# Check network connectivity
docker network ls
docker network inspect orchestratorr_orchestratorr-net

# Test service connectivity
docker-compose exec backend ping frontend
docker-compose exec frontend ping backend

# DNS resolution
docker-compose exec backend nslookup backend
```

## Production Checklist

- [ ] SSL/HTTPS configured
- [ ] Environment variables secured (not in .env)
- [ ] Docker images scanned for vulnerabilities
- [ ] Resource limits set
- [ ] Health checks configured
- [ ] Logging configured and monitored
- [ ] Backup strategy implemented
- [ ] Firewall rules configured
- [ ] Regular update schedule
- [ ] Monitoring/alerting set up
- [ ] Disaster recovery plan documented
- [ ] Non-root user in containers
- [ ] Network isolated from host
- [ ] Secrets not in images or logs

## See Also

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Deployment](https://docs.docker.com/compose/production/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Let's Encrypt for SSL](https://letsencrypt.org/)
