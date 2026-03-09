# App Store - Global State Management

The `appStore.js` module provides the central state management system for the orchestratorr frontend. It handles:

- Application configuration (backend URL, theme, etc.) with localStorage persistence
- Service health status and polling
- Derived state for system health
- User notifications
- Debug utilities

## Stores

### configStore

Writable store for application settings. **Automatically persists to localStorage.**

```javascript
import { configStore } from '$lib/stores';

// Subscribe to changes
configStore.subscribe(config => {
  console.log('Backend URL:', config.backendUrl);
  console.log('Theme:', config.theme);
  console.log('Refresh Interval:', config.refreshInterval);
});

// Update a setting
configStore.update(config => ({
  ...config,
  theme: 'light'
}));
```

**Default Value:**
```javascript
{
  backendUrl: 'http://localhost:8000',
  theme: 'dark',
  refreshInterval: 30,
  showAdvanced: false
}
```

**Helper Functions:**
- `getBackendUrl()` - Get current backend URL
- `setBackendUrl(url)` - Update backend URL
- `resetConfig()` - Reset to defaults

### serviceStatusStore

Writable store for service health status. Updated by `refreshHealth()` and polling.

```javascript
import { serviceStatusStore, refreshHealth } from '$lib/stores';

// Manual refresh
await refreshHealth();

// Subscribe
serviceStatusStore.subscribe(status => {
  console.log(status.radarr.status);    // 'online', 'offline', 'degraded'
  console.log(status.radarr.version);   // '4.7.0'
  console.log(status.radarr.uptime);    // true/false
  console.log(status.lastUpdated);      // Date
  console.log(status.isLoading);        // boolean
});
```

**Structure:**
```javascript
{
  radarr: { status, version, uptime },
  sonarr: { status, version, uptime },
  lidarr: { status, version, uptime },
  prowlarr: { status, version, uptime },
  lastUpdated: Date,
  isLoading: boolean
}
```

### notificationsStore

Writable store for global notifications/alerts.

```javascript
import { addNotification, removeNotification, clearNotifications, notificationsStore } from '$lib/stores';

// Add notification (auto-dismisses after 5s)
addNotification('Settings saved', 'success', 5000);
addNotification('Error loading data', 'error', 5000);

// Add notification with no auto-dismiss
addNotification('Important message', 'info', 0);

// Remove by ID
removeNotification(id);

// Clear all
clearNotifications();
```

**Notification Types:** `'info'`, `'warning'`, `'error'`, `'success'`

## Derived Stores

Derived stores are read-only and update automatically when their dependencies change.

### isSystemHealthy

Returns `true` only if Radarr and at least one other service are online.

```javascript
import { isSystemHealthy } from '$lib/stores';

isSystemHealthy.subscribe(healthy => {
  console.log(healthy ? '✅ System healthy' : '❌ System degraded');
});
```

### onlineServiceCount

Returns the number of services currently online (0-4).

```javascript
import { onlineServiceCount } from '$lib/stores';

onlineServiceCount.subscribe(count => {
  console.log(`${count}/4 services online`);
});
```

### isHealthLoading

Returns `true` while fetching service status.

```javascript
import { isHealthLoading } from '$lib/stores';

isHealthLoading.subscribe(loading => {
  console.log(loading ? 'Loading...' : 'Ready');
});
```

## Polling

### startPolling()

Start automatic polling of service health every 30 seconds.

```javascript
import { startPolling } from '$lib/stores';

startPolling();
```

**Safety Features:**
- Only one polling interval is active at a time
- Safe to call multiple times
- Can be called from multiple components

### stopPolling()

Stop automatic polling.

```javascript
import { stopPolling } from '$lib/stores';

stopPolling();
```

### isPolling()

Check if polling is currently active.

```javascript
import { isPolling } from '$lib/stores';

if (isPolling()) {
  console.log('Polling is active');
}
```

### resetPolling()

Stop and restart polling (useful after config changes).

```javascript
import { resetPolling } from '$lib/stores';

resetPolling();
```

### refreshHealth()

Manually fetch service status immediately (doesn't restart polling interval).

```javascript
import { refreshHealth } from '$lib/stores';

await refreshHealth();
```

## Usage Examples

### Component with Polling

```svelte
<script>
  import { serviceStatusStore, startPolling, stopPolling } from '$lib/stores';
  import { onMount, onDestroy } from 'svelte';

  onMount(() => {
    startPolling();
  });

  onDestroy(() => {
    // Note: stopPolling() stops global polling
    // Only call if you're the last component using it
  });
</script>

{#each Object.entries($serviceStatusStore) as [name, status]}
  <div>{name}: {status.status}</div>
{/each}
```

### Component with Manual Refresh

```svelte
<script>
  import { serviceStatusStore, refreshHealth, isHealthLoading } from '$lib/stores';

  async function handleRefresh() {
    await refreshHealth();
  }
</script>

<button on:click={handleRefresh} disabled={$isHealthLoading}>
  {$isHealthLoading ? 'Refreshing...' : 'Refresh'}
</button>
```

### Component with Settings

```svelte
<script>
  import { configStore, setBackendUrl } from '$lib/stores';

  function updateBackend(newUrl) {
    setBackendUrl(newUrl);
    // Automatically saved to localStorage
  }
</script>

<input bind:value={$configStore.backendUrl} on:change={e => updateBackend(e.target.value)} />
```

### Using SettingsPanel Component

```svelte
<script>
  import SettingsPanel from '$lib/components/SettingsPanel.svelte';
</script>

<SettingsPanel />
```

## localStorage Persistence

The `configStore` automatically persists to localStorage using the prefix `orchestratorr_`.

**Stored Keys:**
- `orchestratorr_config` - Application settings

**Manual localStorage Operations:**

```javascript
// These are internal to appStore, but available if needed:
// Clear a specific key
clearLocalStorage('config');

// This is useful for debugging
localStorage.setItem('orchestratorr_config', JSON.stringify({
  backendUrl: 'http://example.com:8000',
  theme: 'light',
  // ...
}));
```

## Debug Utilities

Enable debug mode to log all state changes:

```javascript
// In browser console
window.DEBUG_ORCHESTRATORR = true;

import { debugAppState } from '$lib/stores';
debugAppState();
```

## Error Handling

All store functions handle errors gracefully:

- Network errors during `refreshHealth()` mark all services as offline
- localStorage errors log warnings but don't crash
- Missing backend URL falls back to default `http://localhost:8000`

## Best Practices

1. **Use derived stores** for derived state instead of subscribing to multiple stores
2. **Keep polling global** - Only call `startPolling()` once per app
3. **Unsubscribe properly** - Use the returned unsubscribe function from `subscribe()`
4. **Prefer `$store` syntax** in Svelte components - Auto-unsubscribes on unmount
5. **Reset on config change** - Call `resetPolling()` after changing `refreshInterval`

Example:
```svelte
<script>
  import { serviceStatusStore } from '$lib/stores';
  // Auto-subscribes and auto-unsubscribes in Svelte
</script>

<p>Status: {$serviceStatusStore.radarr.status}</p>
```

## Architecture

```
appStore.js
├── localStorage utilities
│   ├── createLocalStorageStore()
│   └── clearLocalStorage()
├── configStore (with persistence)
├── serviceStatusStore
├── notificationsStore
├── Derived Stores
│   ├── isSystemHealthy
│   ├── onlineServiceCount
│   └── isHealthLoading
├── Polling Management
│   ├── startPolling()
│   ├── stopPolling()
│   ├── isPolling()
│   └── resetPolling()
├── Health Refresh
│   └── refreshHealth()
└── Utilities
    ├── addNotification()
    ├── removeNotification()
    ├── clearNotifications()
    └── debugAppState()
```

## Testing

When testing components that use appStore:

1. Mock the store subscriptions
2. Test store functions independently
3. Mock fetch for `refreshHealth()`
4. Reset stores between tests

Example (vitest):
```javascript
import { vi } from 'vitest';
import { refreshHealth, serviceStatusStore } from '$lib/stores';

vi.stubGlobal('fetch', vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ radarr: { status: 'online', version: '4.7.0' } })
  })
));

await refreshHealth();
// Assert store was updated
```
