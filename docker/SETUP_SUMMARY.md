# Docker Setup Summary for Orchestratorr

## What's Been Configured ✅

### Core Docker Files

| File | Purpose | Status |
|------|---------|--------|
| `docker-compose.yml` | Production setup | ✅ Complete |
| `docker-compose.dev.yml` | Development with hot reload | ✅ Created |
| `backend/Dockerfile` | Python FastAPI image | ✅ Complete |
| `backend/Dockerfile.dev` | (not needed, uses volume mount) | — |
| `frontend/Dockerfile` | SvelteKit + Nginx production | ✅ Complete |
| `frontend/Dockerfile.dev` | Vite dev server | ✅ Created |
| `backend/.dockerignore` | Exclude unnecessary files | ✅ Complete |
| `frontend/.dockerignore` | Exclude unnecessary files | ✅ Complete |
| `frontend/nginx.conf` | Nginx config with API proxy | ✅ Complete |

### Documentation

| File | Purpose |
|------|---------|
| `docker/README.md` | Complete Docker guide |
| `docker/QUICK_REFERENCE.md` | Quick commands and tips |
| `docker/BEST_PRACTICES.md` | Best practices & security |
| `docker/DEPLOYMENT.md` | Deployment strategies |
| `Makefile` | Easy command shortcuts |

### Key Features

✅ **Multi-stage builds** - Optimized image sizes
✅ **Health checks** - Automatic service monitoring
✅ **Non-root users** - Security hardened containers
✅ **Environment variables** - Easy configuration
✅ **Docker network** - Internal service communication
✅ **Nginx reverse proxy** - API routing from frontend
✅ **Volume mounts** - Development hot reload
✅ **Service dependencies** - Proper startup order
✅ **Restart policies** - Auto-recovery on failure
✅ **Gzip compression** - Optimized frontend delivery
✅ **Security headers** - CORS and X-Frame-Options

## Quick Start

### 1. Setup (First Time Only)

```bash
cd orchestratorr
cp .env.example .env
# Edit .env with your Radarr/Sonarr/Lidarr/Prowlarr details
```

### 2. Production Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

**Access:**
- Frontend: http://localhost
- Backend API: http://localhost:8000/docs

### 3. Development with Hot Reload

```bash
# Start with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Backend and frontend will reload on code changes
```

**Access:**
- Frontend: http://localhost:5173 (Vite dev server)
- Backend: http://localhost:8000/docs

### 4. Using Make (Easier!)

```bash
# Setup
make init          # Create .env file

# Run
make up            # Start services
make down          # Stop services
make dev           # Development mode
make logs          # View logs
make test          # Run tests
make clean         # Remove containers
```

See `Makefile` for all commands.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HOST MACHINE                          │
├─────────────────────────────────────────────────────────┤
│  Docker Network: orchestratorr-net (bridge)             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Frontend Container                              │  │
│  │  Image: orchestratorr-frontend                   │  │
│  │  Port: :80/443 → 0.0.0.0:80                      │  │
│  │  ┌────────────────────────────────────────────┐ │  │
│  │  │ Nginx (Alpine)                             │ │  │
│  │  │ - Serves static SvelteKit build            │ │  │
│  │  │ - Proxies /api/* → backend:8000            │ │  │
│  │  │ - Gzip compression enabled                 │ │  │
│  │  │ - Security headers configured              │ │  │
│  │  └────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Backend Container                              │  │
│  │  Image: orchestratorr-backend                   │  │
│  │  Port: :8000 → 0.0.0.0:8000                     │  │
│  │  ┌────────────────────────────────────────────┐ │  │
│  │  │ Python 3.11 (Slim)                         │ │  │
│  │  │ - FastAPI application                      │ │  │
│  │  │ - Uvicorn ASGI server                      │ │  │
│  │  │ - Radarr/Sonarr/Lidarr proxy               │ │  │
│  │  │ - /health endpoint for monitoring          │ │  │
│  │  │ - Non-root user (appuser:1000)             │ │  │
│  │  └────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
           ↓
    External *arr Services
    (Radarr, Sonarr, etc.)
```

## Environment Configuration

### Required Variables (.env)

```env
# Radarr (required)
RADARR_URL=http://radarr:7878
RADARR_API_KEY=your-api-key

# Optional services
SONARR_URL=http://sonarr:8989
SONARR_API_KEY=your-api-key

LIDARR_URL=http://lidarr:8686
LIDARR_API_KEY=your-api-key

PROWLARR_URL=http://prowlarr:9696
PROWLARR_API_KEY=your-api-key

# Backend config
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=false      # Set to true for development
LOG_LEVEL=INFO             # DEBUG for verbose logging

# Frontend config (optional)
FRONTEND_URL=http://localhost
ALLOWED_ORIGINS=http://localhost,http://localhost:80
```

## Common Tasks

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 50 lines
docker-compose logs --tail 50

# Since specific time
docker-compose logs --since 10m
```

### Execute Commands

```bash
# Backend tests
docker-compose exec backend python -m pytest

# Frontend tests
docker-compose exec frontend npm test

# Backend shell
docker-compose exec backend sh

# Frontend shell
docker-compose exec frontend sh
```

### Restart Services

```bash
# All
docker-compose restart

# Specific
docker-compose restart backend
docker-compose restart frontend

# Force rebuild and restart
docker-compose up -d --build
```

### Check Status

```bash
# Show running containers
docker-compose ps

# Check health
curl http://localhost:8000/health    # Backend
curl http://localhost                # Frontend
curl http://localhost:8000/docs      # API docs

# Resource usage
docker stats
```

## File Structure

```
orchestratorr/
├── .env                        # ← Your configuration (created from .env.example)
├── .env.example                # Example env variables
├── docker-compose.yml          # Production setup
├── docker-compose.dev.yml      # Development setup (hot reload)
├── Makefile                    # Convenient commands
│
├── backend/
│   ├── Dockerfile              # Multi-stage build
│   ├── .dockerignore           # Excludes for build context
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── routes/                 # API routes
│   ├── tests/                  # Unit tests
│   └── ...
│
├── frontend/
│   ├── Dockerfile              # Production (Nginx + static)
│   ├── Dockerfile.dev          # Development (Vite server)
│   ├── .dockerignore           # Excludes for build context
│   ├── nginx.conf              # Nginx configuration
│   ├── package.json            # Node dependencies
│   ├── src/                    # Svelte source
│   ├── tests/                  # Component tests
│   └── ...
│
└── docker/
    ├── README.md               # Full Docker documentation
    ├── QUICK_REFERENCE.md      # Quick command reference
    ├── BEST_PRACTICES.md       # Best practices & security
    ├── DEPLOYMENT.md           # Deployment strategies
    └── SETUP_SUMMARY.md        # ← You are here
```

## Performance Notes

### Image Sizes (Approximate)

- **Backend**: ~250 MB (Python 3.11 slim + dependencies)
- **Frontend**: ~50 MB (Alpine Nginx + static files)
- **Total**: ~300 MB (both images)

### Startup Time

- **Backend**: ~5-10 seconds
- **Frontend**: ~3-5 seconds
- **Total**: ~10-15 seconds to fully ready

### Resource Usage

- **Backend**: 256 MB - 512 MB RAM (recommended)
- **Frontend**: 64 MB - 128 MB RAM (recommended)
- **Network**: Minimal (API calls only)

## Security Features

✅ Non-root user in containers
✅ Read-only root filesystem (optional)
✅ Security headers (X-Frame-Options, X-Content-Type-Options)
✅ No hardcoded secrets
✅ .env excluded from build context
✅ Healthchecks for service monitoring
✅ Network isolation (private bridge network)
✅ No exposed unnecessary ports

## Troubleshooting

### Quick Diagnostics

```bash
# Validate configuration
docker-compose config --quiet

# Check if services are running
docker-compose ps

# View error logs
docker-compose logs backend | grep -i error
docker-compose logs frontend | grep -i error

# Test connectivity between services
docker-compose exec backend ping frontend
docker-compose exec frontend ping backend
```

### Common Issues

| Problem | Solution |
|---------|----------|
| Port already in use | Edit `docker-compose.yml`, change ports |
| Backend unreachable | Check `.env` URLs, verify backend running |
| Frontend shows 502 | Backend not ready, check health check |
| Environment not loading | Verify `.env` file exists and is readable |
| Disk space | Run `docker system prune -a` |
| Memory issues | Reduce replicas, add resource limits |

See `docker/DEPLOYMENT.md` for more troubleshooting.

## Next Steps

1. **Configure your environment** - Edit `.env` with your Radarr/Sonarr/Lidarr URLs
2. **Start services** - Run `docker-compose up -d`
3. **Verify health** - Check `docker-compose ps` shows healthy services
4. **Access dashboard** - Open http://localhost in browser
5. **Read documentation** - Check `docker/README.md` for detailed guide

## Getting Help

- **Quick commands**: See `docker/QUICK_REFERENCE.md`
- **Detailed guide**: Read `docker/README.md`
- **Best practices**: Check `docker/BEST_PRACTICES.md`
- **Deployment**: Review `docker/DEPLOYMENT.md`
- **Makefile**: Run `make help` for all available commands

## Summary

Your project now has:
- ✅ Production-ready Docker Compose setup
- ✅ Development setup with hot reload
- ✅ Comprehensive documentation
- ✅ Easy Makefile commands
- ✅ Security best practices
- ✅ Health checks and monitoring
- ✅ Multi-stage optimized builds

**You're ready to deploy!** 🚀
