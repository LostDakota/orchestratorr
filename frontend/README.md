# Orchestratorr Frontend

A professional, real-time monitoring dashboard for the *arr suite, built with Svelte 5 and Tailwind CSS.

## Components

### StatusGrid.svelte

The main dashboard component that displays real-time service status for all configured *arr services.

**Features:**
- Real-time status updates (polls every 30 seconds)
- Service health indicators (online, offline, degraded)
- Version information display
- Last-checked timestamps
- Global error banner for backend connectivity issues
- Manual refresh button
- Dark theme with industrial aesthetic

**Usage:**

```svelte
<script>
  import StatusGrid from '$lib/components/StatusGrid.svelte';
</script>

<StatusGrid />
```

### StatusBadge.svelte

A reusable component that displays service status with a visual indicator.

**Props:**
- `status` (string): Status value - `'online'`, `'offline'`, `'degraded'`, or `'unknown'`
- `compact` (boolean, optional): If true, uses smaller sizing for inline display (default: false)

**Status Indicators:**
- **Online** 🟢: Pulsing green dot, "Operational"
- **Offline** 🔴: Static red dot, "Connection Failed"
- **Degraded** 🟡: Static yellow dot, "Slow Response"
- **Unknown** ⚪: Static gray dot, "Unknown"

**Usage:**

```svelte
<script>
  import StatusBadge from '$lib/components/StatusBadge.svelte';
</script>

<StatusBadge status="online" />
<StatusBadge status="offline" compact={true} />
```

## Stores

### statusStore

A Svelte writable store containing the current status of all *arr services.

**Store Structure:**

```javascript
{
  radarr: { version: string, status: 'online'|'offline'|'degraded'|'unknown', lastChecked: Date },
  sonarr: { version: string, status: 'online'|'offline'|'degraded'|'unknown', lastChecked: Date },
  lidarr: { version: string, status: 'online'|'offline'|'degraded'|'unknown', lastChecked: Date },
  prowlarr: { version: string, status: 'online'|'offline'|'degraded'|'unknown', lastChecked: Date },
  backendError: null | string
}
```

### isAnyServiceDown

A derived store that returns `true` if any service is offline or the backend is unreachable.

### initializeStatusPolling()

Initializes automatic polling of service status every 30 seconds.

**Returns:** Cleanup function to stop polling

**Usage:**

```javascript
import { initializeStatusPolling } from '$lib/stores';

onMount(() => {
  const stopPolling = initializeStatusPolling();
  return stopPolling; // Cleanup on unmount
});
```

### refreshStatus()

Manually trigger an immediate status refresh without waiting for the next polling interval.

**Usage:**

```javascript
import { refreshStatus } from '$lib/stores';

await refreshStatus();
```

## Configuration

### API Base URL

Edit `frontend/src/lib/stores/statusStore.js` to change the FastAPI backend URL:

```javascript
const API_BASE = 'http://localhost:8000/api/v1'; // Change this
```

### Polling Interval

Edit the polling interval (in milliseconds):

```javascript
const POLL_INTERVAL = 30000; // 30 seconds
```

### Service Timeout

Individual service requests timeout after 5 seconds (per service). Adjust in `fetchServiceStatus()`:

```javascript
const timeout = 5000; // 5 seconds
```

## Styling

All components use **Tailwind CSS** with a dark theme (`bg-gray-900`). Key color scheme:

- **Online**: Green 500/200 (`bg-green-500`, `text-green-200`)
- **Offline**: Red 500/200 (`bg-red-500`, `text-red-200`)
- **Degraded**: Yellow 500/200 (`bg-yellow-500`, `text-yellow-200`)
- **Background**: Gray 800-900

Customize colors by editing the `statusConfig` object in `StatusBadge.svelte` and Tailwind classes in components.

## Memory Management

All components properly clean up resources on unmount:
- Polling interval is cleared when the component is destroyed
- Store subscriptions are unsubscribed
- No memory leaks

## Requirements

- Svelte 5 (or current stable)
- Tailwind CSS 3+
- Backend FastAPI server running at the configured URL
- Endpoints: `/api/v1/{service}/system/status` for each service

## Development

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build
```

## Error Handling

- If the FastAPI backend is unreachable, a red alert banner appears at the top
- Individual service connection timeouts fall back to "offline" status
- Response times >3 seconds trigger "degraded" status
- All errors are gracefully handled without breaking the UI
