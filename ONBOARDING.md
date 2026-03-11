# Orchestratorr Onboarding Wizard

Interactive CLI wizard for securely configuring your Orchestratorr instance.

## Quick Start

### Method 1: Using Make (Recommended)

```bash
make onboard
```

### Method 2: Direct Python

```bash
cd backend
python onboard.py
```

## What the Wizard Does

The onboarding wizard guides you through configuring your media server setup:

1. **Prompts for service credentials** — URLs and API keys for:
   - **Radarr** (movies) — required
   - **Sonarr** (TV shows) — optional
   - **Lidarr** (music) — optional
   - **Prowlarr** (indexer management) — optional

2. **Tests connections** — Verifies each service is reachable with valid credentials

3. **Configures FastAPI** — Host and port for the backend API server

4. **Configures frontend** — Frontend URL and allowed origins for CORS

5. **Securely saves configuration** — Stores everything in `.env` file with:
   - **Permissions: 0600** (owner read/write only)
   - **Location**: Project root directory
   - **Security**: Never committed to version control (.gitignore protected)

## Configuration Storage

Your credentials are stored in:
```
/path/to/orchestratorr/.env
```

### Security Features

- **File Permissions**: `.env` file is created with `0600` permissions (readable/writable only by the owner)
- **Not Version Controlled**: `.env` is in `.gitignore` and will never be committed
- **Password Input**: API keys are masked during entry (not displayed on screen)
- **Connection Testing**: Optional validation of credentials before saving

### What NOT to Do

🚫 **Never:**
- Commit `.env` to version control
- Share your `.env` file
- Run the wizard with world-readable permissions
- Store API keys in plain text elsewhere

✅ **Do:**
- Keep `.env` on your machine only
- Use unique API keys for each service
- Rotate API keys periodically
- Back up `.env` in a secure location

## Configuration Reference

After running the wizard, your `.env` file will contain:

```env
# Service URLs and API Keys
RADARR_URL=http://localhost:7878
RADARR_API_KEY=your-api-key

SONARR_URL=http://localhost:8989
SONARR_API_KEY=your-api-key

LIDARR_URL=http://localhost:8686
LIDARR_API_KEY=your-api-key

PROWLARR_URL=http://localhost:9696
PROWLARR_API_KEY=your-api-key

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

## Default Service Ports

These are the standard ports for *arr services. Adjust if you're running on different ports:

| Service | Default Port |
|---------|-------------|
| Radarr | 7878 |
| Sonarr | 8989 |
| Lidarr | 8686 |
| Prowlarr | 9696 |

## Getting API Keys

### Radarr / Sonarr / Lidarr / Prowlarr

1. Open the service's web interface
2. Go to **Settings** → **General**
3. Scroll to **Security** section
4. Copy the **API Key** value
5. Paste it when prompted by the wizard

## Troubleshooting

### "Cannot connect to [service]"

- Ensure the service is running and accessible at the provided URL
- Check firewall rules if accessing from a remote machine
- Verify the API key is correct
- Try `http://localhost:PORT` if using default local setup

### "Unauthorized (invalid API key)"

- Double-check the API key in the service's settings
- Make sure you copied the entire key (no spaces)
- Regenerate the API key in the service if needed

### "Connection timeout"

- Service may be unresponsive or slow
- Check service logs for errors
- Try with a longer timeout or configure offline

## Manual Configuration

If you prefer to configure manually:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your text editor:
   ```bash
   nano .env
   ```

3. Set file permissions:
   ```bash
   chmod 600 .env
   ```

## Next Steps

After running the onboarding wizard:

1. Start the services:
   ```bash
   make dev      # Development mode with hot reload
   # or
   make up       # Production mode
   ```

2. Access the application:
   - **Frontend**: http://localhost:5173 (dev) or http://localhost (prod)
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

3. Test the setup by searching for content in the frontend

## Security Considerations

- **Keep `.env` private** — This file contains your API keys
- **Use strong, unique API keys** — Don't reuse keys across services
- **Rotate keys periodically** — Change API keys every 6-12 months
- **Monitor access logs** — Check service logs for unauthorized access attempts
- **Use HTTPS in production** — Configure SSL certificates for remote access
- **Firewall your services** — Don't expose services directly to the internet; use VPN or reverse proxy

## Environment Variables

The `.env` file is automatically loaded by the application on startup. All variables are optional except for Radarr (which provides the base movie library).

For more information, see:
- [Backend Configuration](backend/config.py)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
