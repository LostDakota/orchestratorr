# Docker Quick Reference

## One-Liner Setup

```bash
git clone <repo> && cd orchestratorr && cp .env.example .env && docker-compose up -d
```

## Common Commands

### Start/Stop

```bash
docker-compose up -d              # Start all services in background
docker-compose down               # Stop and remove containers
docker-compose stop               # Stop without removing
docker-compose restart            # Restart all services
docker-compose restart backend    # Restart specific service
```

### Logs

```bash
docker-compose logs -f            # All logs, follow
docker-compose logs backend       # Backend only
docker-compose logs frontend -f   # Frontend, follow
docker-compose logs --tail 50     # Last 50 lines
docker-compose logs --since 10m   # Last 10 minutes
```

### Status

```bash
docker-compose ps                 # Show running services
docker-compose ps -a              # Include stopped
docker image ls | grep orchestr   # Show images
docker volume ls | grep orchestr  # Show volumes
docker network ls | grep orchestr # Show networks
```

### Execute Commands

```bash
docker-compose exec backend python -m pytest            # Run backend tests
docker-compose exec backend python -c "import sys"     # Quick Python check
docker-compose exec frontend npm test                   # Run frontend tests
docker-compose exec frontend npm run build              # Build frontend
```

### Shell Access

```bash
docker-compose exec backend sh    # Backend shell
docker-compose exec frontend sh   # Frontend shell
docker-compose exec backend bash  # Backend bash (if available)
```

### Rebuild

```bash
docker-compose build              # Build images
docker-compose build --no-cache   # Force rebuild
docker-compose build --pull       # Pull fresh base images
docker-compose up -d --build      # Build then start
```

### Clean Up

```bash
docker-compose down -v            # Remove containers + volumes
docker-compose down --rmi all     # Remove containers + images
docker image prune -a             # Remove unused images
docker volume prune               # Remove unused volumes
docker system prune -a            # Everything unused
```

## Environment Setup

```bash
# Copy example and edit
cp .env.example .env

# Edit with your values
nano .env

# Check environment in container
docker-compose exec backend env | grep RADARR
```

## Access Points

| Service   | URL                        | Purpose           |
|-----------|----------------------------|-------------------|
| Frontend  | http://localhost           | Web UI            |
| Backend   | http://localhost:8000      | API               |
| API Docs  | http://localhost:8000/docs | Swagger UI        |
| API Docs  | http://localhost:8000/redoc| ReDoc UI          |
| Health    | http://localhost:8000/health| Backend health    |

## Development Workflow

```bash
# Use dev compose for hot reload
docker-compose -f docker-compose.dev.yml up

# Backend will reload on code changes
# Frontend available at http://localhost:5173

# For quick iteration, edit then:
docker-compose restart backend

# Or rebuild if dependencies changed:
docker-compose build backend && docker-compose restart backend
```

## Production Deployment

```bash
# Build images with fresh layers
docker-compose build --pull --no-cache

# Start in background
docker-compose up -d

# Monitor logs
docker-compose logs -f

# Check health
docker-compose ps                    # Should show (healthy)
curl http://localhost:8000/health    # Should return 200
curl http://localhost                # Should return frontend
```

## Troubleshooting Quick Fixes

```bash
# Backend won't start?
docker-compose logs backend | tail -20

# Frontend showing 502?
docker-compose ps                           # Backend running?
docker-compose exec frontend ping backend   # Can reach backend?

# Port conflicts?
lsof -i :80 && lsof -i :8000

# Need to reset everything?
docker-compose down -v --rmi all && docker-compose up -d --build

# Disk space issues?
docker system prune -a

# Memory issues?
docker stats
```

## Environment Variables Reference

```env
# Backend
RADARR_URL=http://radarr:7878
RADARR_API_KEY=your-key
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=false
LOG_LEVEL=INFO

# Frontend  
VITE_API_BASE=http://localhost:8000  # Or empty for relative paths

# Optional (future services)
SONARR_URL=http://sonarr:8989
SONARR_API_KEY=your-key
```

## Docker Compose File Locations

```
orchestratorr/
├── docker-compose.yml           # Production
├── docker-compose.dev.yml       # Development (hot reload)
├── backend/
│   ├── Dockerfile               # Production build
│   └── .dockerignore
├── frontend/
│   ├── Dockerfile               # Production (nginx)
│   ├── Dockerfile.dev           # Development (vite)
│   └── .dockerignore
└── docker/
    ├── README.md                # Full documentation
    ├── BEST_PRACTICES.md        # Best practices
    └── QUICK_REFERENCE.md       # This file
```

## Network Details

```bash
# View network
docker network inspect orchestratorr_orchestratorr-net

# Service names (from inside containers)
backend:8000    # Backend service
frontend:80     # Frontend service

# From host
localhost:8000  # Backend
localhost:80    # Frontend
```

## Useful Docker Inspect Commands

```bash
# Inspect service config
docker-compose config

# Validate compose file
docker-compose config --quiet

# Show compose project status
docker-compose ls

# Follow all logs with timestamps
docker-compose logs -f -t

# Get container IDs
docker-compose ps -q

# Get specific service container ID
docker-compose ps -q backend
```

## Advanced Patterns

### Multiple Instances

```bash
# Run with different project name
docker-compose -p orchestratorr-prod up -d
docker-compose -p orchestratorr-staging up -d

# See all projects
docker-compose ls
```

### Selective Services

```bash
# Only start backend
docker-compose up -d backend

# Only restart frontend
docker-compose restart frontend

# Logs from multiple services
docker-compose logs backend frontend
```

### Environment Overrides

```bash
# Use different .env file
docker-compose --env-file .env.prod up -d

# Override single variable
RADARR_API_KEY=new-key docker-compose up -d
```

## Performance Tips

- Use `--no-cache` only when needed (slows builds)
- Let Docker cache layers between builds
- Mount volumes only when necessary
- Use `.dockerignore` to reduce build context
- Rebuild services independently (don't rebuild all)
- Use health checks to verify startup

## Docker Compose Syntax

```yaml
# Min version 3.8 (recommended)
version: '3.8'

services:
  service-name:
    build: ./path           # Build from Dockerfile
    image: name:tag         # OR use prebuilt image
    container_name: name    # Custom container name
    restart: unless-stopped # Restart policy
    ports:
      - "host:container"    # Port mapping
    environment:
      KEY: value            # Environment variables
    env_file: .env          # Load from file
    volumes:
      - ./host:/container   # Volume mount
    depends_on:
      - other-service       # Start after this
    healthcheck:
      test: ["CMD", "curl", "localhost"]
      interval: 30s
      timeout: 3s
      retries: 3
    networks:
      - network-name        # Custom network

networks:
  network-name:
    driver: bridge
```

## See Also

- Full docs: `docker/README.md`
- Best practices: `docker/BEST_PRACTICES.md`
- Official docs: https://docs.docker.com/
