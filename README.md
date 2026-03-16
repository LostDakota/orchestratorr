# 🎭 Orchestratorr

**A unified front-end dashboard for managing your *arr suite** — Radarr, Sonarr, Lidarr, and Prowlarr in one powerful interface.

## 🚨 Project Status: In Active Development

### ✨ Current Features

#### Services Supported
- [x] Radarr (Movies)
  - Full status monitoring
  - Movie library browsing
  - Unified media search
  - Movie search and addition 
  - Movie metadata refresh
- [x] Sonarr (TV Shows)
  - Status monitoring
  - Series library browsing
- [x] Lidarr (Music)
  - Status monitoring
  - Artist library browsing
- [x] Prowlarr (Indexers)
  - Status monitoring
  - Indexer management

#### Dashboard Functionality
- [x] Unified service status dashboard
- [x] Real-time service health monitoring
- [x] Universal search 
- [x] Media search and addition
- [x] Responsive design

### 🚧 Upcoming/Missing Features

#### Media Management
- [x] Media search across services
- [x] Basic media addition
- [ ] Enhanced media addition workflow
  - [ ] Quality profile selection
  - [ ] Root folder selection
- [ ] Bulk media addition
- [ ] Media details and metadata editing

#### Recent Activity
- [x] Basic recent activity display (mock data)
- [ ] Real-time activity tracking
- [ ] Detailed activity logs
- [ ] Filtering and searching activity

#### Disk Space
- [x] Basic disk space display (mock data)
- [ ] Multiple storage location support
- [ ] Detailed storage breakdown
- [ ] Storage trend analysis
- [ ] Low disk space alerts

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser / Frontend                       │
│                    SvelteKit on Port 5173                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Dashboard    │ Service Cards  │ Search  │ Add Media  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬──────────────────────────────────────────┘
                     │ HTTP/REST API Calls
                     │ (localhost:8000)
┌────────────────────▼──────────────────────────────────────────┐
│                  Backend / Proxy Server                        │
│                  FastAPI on Port 8000                          │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ /api/v1/media/search                               │     │
│  │ /api/v1/media/add                                  │     │
│  │ Proxy routes for each *arr service                 │     │
│  └──────────────────────────────────────────────────────┘     │
└────────┬──────────────────┬──────────────────┬───────────────┘
         │                  │                  │
    ┌────▼──┐          ┌────▼──┐         ┌────▼──┐
    │ Radarr│          │ Sonarr│         │ Lidarr│  (Optional)
    └───────┘          └───────┘         └───────┘
```

## 🌟 Features Deep Dive

### 📡 Media Search
- Search movies via TMDB
- Real-time results with poster, overview, release date
- One-click addition to library
- Supports filtering and pagination

### 🖥️ Dashboard
- Comprehensive service status overview
- Auto-refreshing health checks
- Responsive design for desktop and mobile

## 🔧 Upcoming Improvements

1. Enhanced media search
2. More service integrations
3. Advanced filtering
4. Personalization options
5. Performance optimizations

## 🌐 Supported Services

- **Radarr**: Movies
- **Sonarr**: TV Shows
- **Lidarr**: Music
- **Prowlarr**: Indexers

## 📋 Requirements

- Python 3.10+
- Node.js 18+
- Docker (optional)

## 🚀 Quick Start

1. Clone the repository
2. Set up backend: `cd backend && pip install -r requirements.txt`
3. Set up frontend: `cd frontend && npm install`
4. Configure `.env` with service URLs and API keys
5. Start backend: `uvicorn backend.main:app --reload`
6. Start frontend: `npm run dev`

## 🤝 Contributions Welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Happy Media Management!** 🎬📺🎵