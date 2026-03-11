# 🎭 Orchestratorr

**A unified front-end dashboard for managing your *arr suite** — Radarr, Sonarr, Lidarr, and Prowlarr all in one beautiful, responsive interface.

## ✨ Features

- **🎬 Unified Dashboard**: Monitor all your *arr services in real-time from one place
- **📊 Service Health Status**: See at a glance which services are online and operational
- **🔍 Universal Search**: Search across all *arr services simultaneously
- **💾 Disk Space Monitoring**: Track storage usage across your media library
- **📱 Responsive Design**: Works beautifully on desktop, tablet, and mobile devices
- **🔄 Auto-Refresh**: Real-time polling every 30 seconds to keep data current
- **⚙️ Settings Panel**: Configure backend URL and preferences without editing files
- **🚀 Fast & Modern**: Built with SvelteKit and FastAPI for optimal performance

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser / Frontend                       │
│                    SvelteKit on Port 5173                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Dashboard    │ Service Cards  │ Search  │ Settings   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬──────────────────────────────────────┘
                         │ HTTP/REST API Calls
                         │ (localhost:8000)
┌────────────────────────▼──────────────────────────────────────┐
│                  Backend / Proxy Server                        │
│                  FastAPI on Port 8000                          │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ /api/v1/proxy/status     → Aggregate Status         │     │
│  │ /api/v1/proxy/radarr/*   → Radarr API Proxy         │     │
│  │ /api/v1/proxy/sonarr/*   → Sonarr API Proxy         │     │
│  │ /api/v1/proxy/lidarr/*   → Lidarr API Proxy         │     │
│  │ /api/v1/proxy/prowlarr/* → Prowlarr API Proxy       │     │
│  └──────────────────────────────────────────────────────┘     │
└────────┬──────────────────┬──────────────────┬───────────────┘
         │                  │                  │
    ┌────▼──┐          ┌────▼──┐         ┌────▼──┐
    │ Radarr│          │ Sonarr│         │ Lidarr│  (Optional)
    └───────┘          └───────┘         └───────┘
```

## 📋 Requirements

### Minimum
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher
- **Radarr**: Running and accessible (required)

### Optional
- **Sonarr**: For TV show management
- **Lidarr**: For music management
- **Prowlarr**: For indexer management

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/LostDakota/orchestratorr.git
cd orchestratorr
```

### 2. Backend Setup

```bash
# Create Python virtual environment
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env and add your *arr URLs and API keys
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

### 4. Start Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the dashboard:**
- 🌐 Frontend: http://localhost:5173
- 🔌 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

## 🐳 Docker Deployment

Orchestratorr can be run entirely via Docker Compose for easy deployment.

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Quick Start with Docker

1. **Clone and configure**:
   ```bash
   git clone https://github.com/LostDakota/orchestratorr.git
   cd orchestratorr
   cp .env.example .env
   # Edit .env and add your *arr service URLs and API keys
   ```

2. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Access the dashboard**:
   - 🌐 Frontend: http://localhost:80
   - 🔌 Backend API: http://localhost:8000
   - 📚 API Docs: http://localhost:8000/docs

4. **View logs**:
   ```bash
   docker-compose logs -f
   ```

5. **Stop services**:
   ```bash
   docker-compose down
   ```

### Docker Compose Configuration

The `docker-compose.yml` file defines two services:

- **backend**: FastAPI application on port 8000
- **frontend**: Nginx serving SvelteKit static files on port 80

Nginx proxies `/api/*` requests to the backend, allowing the frontend to make relative API calls.

### Environment Variables

Create a `.env` file in the project root with your *arr service configurations:

```bash
# Radarr (REQUIRED)
RADARR_URL=http://localhost:7878
RADARR_API_KEY=your_radarr_api_key_here

# Sonarr (Optional)
SONARR_URL=http://localhost:8989
SONARR_API_KEY=your_sonarr_api_key_here

# Lidarr (Optional)
LIDARR_URL=http://localhost:8686
LIDARR_API_KEY=your_lidarr_api_key_here

# Prowlarr (Optional)
PROWLARR_URL=http://localhost:9696
PROWLARR_API_KEY=your_prowlarr_api_key_here

# Backend Configuration (Docker defaults)
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
LOG_LEVEL=INFO
```

### Building Images Manually

You can also build Docker images individually:

```bash
# Build backend
cd backend
docker build -t orchestratorr-backend .

# Build frontend
cd frontend
docker build -t orchestratorr-frontend --build-arg VITE_API_BASE="" .
```

### Docker Compose Commands

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start services in background |
| `docker-compose down` | Stop and remove containers |
| `docker-compose logs -f` | Follow logs |
| `docker-compose ps` | Show service status |
| `docker-compose build` | Rebuild images |
| `docker-compose restart` | Restart services |

## 📁 Project Structure

```
orchestratorr/
├── frontend/                      # SvelteKit Frontend Application
│   ├── src/
│   │   ├── app.html              # HTML template
│   │   ├── App.svelte            # Root component
│   │   ├── routes/
│   │   │   └── dashboard/
│   │   │       └── +page.svelte  # Main dashboard page
│   │   └── lib/
│   │       ├── components/       # Reusable UI components
│   │       │   ├── StatusGrid.svelte
│   │       │   ├── ServiceCard.svelte
│   │       │   ├── UniversalSearch.svelte
│   │       │   └── ...
│   │       └── stores/           # Svelte stores for state management
│   │           ├── appStore.js   # Global app state, API calls
│   │           └── statusStore.js
│   ├── package.json
│   ├── svelte.config.js
│   └── vitest.config.js
│
├── backend/                       # FastAPI Backend Application
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Configuration & environment variables
│   ├── requirements.txt          # Python dependencies
│   ├── routes/
│   │   ├── proxy.py             # Main proxy routes (/api/v1/proxy/*)
│   │   └── search.py            # Search functionality
│   ├── clients/
│   │   └── radarr.py            # Radarr API client
│   ├── schemas/                  # Pydantic models
│   └── tests/                    # Unit and integration tests
│
├── docker/                        # Docker configuration (optional)
├── .env.example                   # Example environment variables
├── .env                           # Your local configuration (NOT in git)
├── .gitignore
└── README.md
```

## ⚙️ Configuration

### Backend Environment Variables (.env)

```bash
# Radarr (REQUIRED)
RADARR_URL=http://localhost:7878
RADARR_API_KEY=your_radarr_api_key_here

# Sonarr (Optional)
SONARR_URL=http://localhost:8989
SONARR_API_KEY=your_sonarr_api_key_here

# Lidarr (Optional)
LIDARR_URL=http://localhost:8686
LIDARR_API_KEY=your_lidarr_api_key_here

# Prowlarr (Optional)
PROWLARR_URL=http://localhost:9696
PROWLARR_API_KEY=your_prowlarr_api_key_here

# Server Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=true

# Frontend Configuration
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000`. To change:

1. **Development**: Edit in `src/lib/stores/appStore.js` (default: `http://localhost:8000`)
2. **Settings Panel**: Use the ⚙️ settings button in the dashboard UI

## 🔌 API Endpoints

### Health & Status

- `GET /health` - Basic health check
- `GET /api/v1/health` - API-specific health check
- `GET /api/v1/proxy/status` - Aggregated status of all *arr services

### Radarr Endpoints

- `GET /api/v1/proxy/radarr/status` - Get Radarr system status
- `GET /api/v1/proxy/radarr/movies` - Get all movies
- `GET /api/v1/proxy/radarr/movies/{id}` - Get movie by ID
- `GET /api/v1/proxy/radarr/calendar` - Get upcoming releases
- `POST /api/v1/proxy/radarr/movies` - Add new movie
- `POST /api/v1/proxy/radarr/command/search` - Search for missing movies
- `POST /api/v1/proxy/radarr/command/refresh` - Refresh movie metadata
- `DELETE /api/v1/proxy/radarr/movies/{id}` - Remove movie

### Sonarr, Lidarr, Prowlarr

Similar endpoints are available for other services once their clients are implemented.

## 🧪 Development

### Running Tests

```bash
# Backend tests
cd backend
.venv/bin/python -m pytest tests/

# Frontend tests
cd ../frontend
npm run test
npm run test:coverage
```

### Code Quality

```bash
# Backend
cd backend
.venv/bin/python -m black .           # Format
.venv/bin/python -m flake8 .          # Lint
.venv/bin/python -m mypy .            # Type check
.venv/bin/python -m isort .           # Sort imports

# Frontend
cd ../frontend
npm run check                          # svelte-check
```

### Building for Production

```bash
# Frontend build
cd frontend
npm run build

# Backend can be run with gunicorn or similar
cd ../backend
.venv/bin/pip install gunicorn
.venv/bin/gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## 🔧 Troubleshooting

### Frontend can't connect to backend

**Problem**: Dashboard shows "offline" for all services even though they're running

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in `.env`: `ALLOWED_ORIGINS` should include frontend URL
3. Check browser console for CORS errors (F12)
4. Verify firewall isn't blocking port 8000
5. If using different IP/hostname, update `src/lib/stores/appStore.js`

### Backend can't reach *arr services

**Problem**: Backend returns "offline" status for services

**Solutions**:
1. Verify *arr services are running
2. Check URLs in `.env` are correct (test with `curl http://radarr_url/api/v3/system/status`)
3. Verify API keys in `.env` are correct
4. Check firewall/network connectivity to *arr services
5. Review backend logs: `LOG_LEVEL=DEBUG` in `.env`

### Port already in use

```bash
# Find process using port
lsof -i :8000    # Backend
lsof -i :5173    # Frontend

# Kill process if needed
kill -9 <PID>
```

### Virtual environment not activating

```bash
# Ensure you're in the backend directory
cd backend

# Linux/Mac
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat
```

## 📚 Additional Resources

- **Radarr API Docs**: https://radarr.servarr.com/docs/api/
- **Sonarr API Docs**: https://sonarr.servarr.com/docs/api/
- **Lidarr API Docs**: https://lidarr.servarr.com/docs/api/
- **Prowlarr API Docs**: https://prowlarr.servarr.com/docs/api/
- **SvelteKit Docs**: https://kit.svelte.dev/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Built for managing multiple [*arr](https://wiki.servarr.com/) applications
- Inspired by the amazing *arr community
- Uses [SvelteKit](https://kit.svelte.dev/) and [FastAPI](https://fastapi.tiangolo.com/)

---

**Have questions or issues?** Open an issue on GitHub or check the troubleshooting section above.

**Happy organizing!** 🎬📺🎵