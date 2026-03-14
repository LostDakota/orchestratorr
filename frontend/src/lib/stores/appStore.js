/**
 * Global application state management.
 *
 * Manages all global application state including:
 * - Configuration (backend URL, UI preferences)
 * - Service health status
 * - System-wide loading states
 * - Polling lifecycle
 */

import { writable, derived } from 'svelte/store';

const POLL_INTERVAL = 30000; // 30 seconds
const STORAGE_KEY_PREFIX = 'orchestratorr_';

/**
 * Utility: Create a writable store with localStorage persistence.
 *
 * Automatically syncs store updates to localStorage and loads initial value
 * from localStorage on creation.
 *
 * @param {string} key - localStorage key (without prefix)
 * @param {*} initialValue - Default value if not in localStorage
 * @returns {import('svelte/store').Writable} Writable store with persistence
 */
function createLocalStorageStore(key, initialValue) {
	const storageKey = `${STORAGE_KEY_PREFIX}${key}`;

	// Try to load from localStorage
	let initialData = initialValue;
	if (typeof window !== 'undefined' && localStorage) {
		try {
			const storedValue = localStorage.getItem(storageKey);
			if (storedValue) {
				initialData = JSON.parse(storedValue);
			}
		} catch (error) {
			console.warn(`Failed to load ${key} from localStorage:`, error);
		}
	}

	const store = writable(initialData);

	// Subscribe to store changes and sync to localStorage
	store.subscribe((value) => {
		if (typeof window !== 'undefined' && localStorage) {
			try {
				localStorage.setItem(storageKey, JSON.stringify(value));
			} catch (error) {
				console.warn(`Failed to save ${key} to localStorage:`, error);
			}
		}
	});

	return store;
}

/**
 * Utility: Clear a localStorage item.
 *
 * @param {string} key - localStorage key (without prefix)
 */
function clearLocalStorage(key) {
	if (typeof window !== 'undefined' && localStorage) {
		try {
			localStorage.removeItem(`${STORAGE_KEY_PREFIX}${key}`);
		} catch (error) {
			console.warn(`Failed to clear ${key} from localStorage:`, error);
		}
	}
}

// ============================================================================
// Application Configuration Store
// ============================================================================

/**
 * Get environment variable for API base URL
 */
const getEnvApiBase = () => {
	// Check if VITE_API_BASE is defined (including empty string)
	if (import.meta.env.VITE_API_BASE !== undefined) {
		return import.meta.env.VITE_API_BASE;
	}
	return 'http://localhost:8000';
};

/**
 * Get environment variable for service URLs
 */
export const getEnvServiceUrls = () => {
	return {
		radarrUrl: import.meta.env.VITE_RADARR_URL || 'http://localhost:7878',
		sonarrUrl: import.meta.env.VITE_SONARR_URL || 'http://localhost:8989',
		lidarrUrl: import.meta.env.VITE_LIDARR_URL || 'http://localhost:8686',
		prowlarrUrl: import.meta.env.VITE_PROWLARR_URL || 'http://localhost:9696',
	};
};

/**
 * Application configuration store.
 *
 * Persists to localStorage automatically.
 *
 * @type {import('svelte/store').Writable<{
 *   backendUrl: string,
 *   theme: 'light' | 'dark',
 *   refreshInterval: number,
 *   showAdvanced: boolean
 * }>}
 */
export const configStore = createLocalStorageStore('config', {
	backendUrl: getEnvApiBase(),
	theme: 'dark',
	refreshInterval: 30,
	showAdvanced: false,
});

/**
 * Get the current backend URL from config.
 *
 * @returns {Promise<string>} Current backend URL
 */
export async function getBackendUrl() {
	let url = '';
	configStore.subscribe((config) => {
		url = config.backendUrl;
	});
	return url;
}

/**
 * Update the backend URL.
 *
 * @param {string} url - New backend URL
 */
export function setBackendUrl(url) {
	configStore.update((config) => ({
		...config,
		backendUrl: url,
	}));
}

/**
 * Reset configuration to defaults.
 */
export function resetConfig() {
	configStore.set({
		backendUrl: getEnvApiBase(),
		theme: 'dark',
		refreshInterval: 30,
		showAdvanced: false,
	});
	clearLocalStorage('config');
}

// ============================================================================
// Service Health Store
// ============================================================================

/**
 * Service health status store.
 *
 * Tracks the online/offline status and metadata for all *arr services.
 * Updated by refreshHealth() and automatic polling.
 *
 * @type {import('svelte/store').Writable<{
 *   radarr: { status: string, version?: string, uptime?: boolean },
 *   sonarr: { status: string, version?: string, uptime?: boolean },
 *   lidarr: { status: string, version?: string, uptime?: boolean },
 *   prowlarr: { status: string, version?: string, uptime?: boolean },
 *   lastUpdated?: Date,
 *   isLoading?: boolean
 * }>}
 */
export const serviceStatusStore = writable({
	radarr: { status: 'unknown', version: null, uptime: false },
	sonarr: { status: 'unknown', version: null, uptime: false },
	lidarr: { status: 'unknown', version: null, uptime: false },
	prowlarr: { status: 'unknown', version: null, uptime: false },
	lastUpdated: null,
	isLoading: false,
});

/**
 * Manually fetch service health status from the backend.
 *
 * Calls GET /api/v1/proxy/status and updates serviceStatusStore.
 * Handles errors gracefully and marks services as offline if unreachable.
 *
 * @returns {Promise<void>}
 */
export async function refreshHealth() {
	serviceStatusStore.update((store) => ({
		...store,
		isLoading: true,
	}));

	try {
		let backendUrl = '';
		configStore.subscribe((config) => {
			backendUrl = config.backendUrl;
		});

		const response = await fetch(`${backendUrl}/api/v1/status`, {
			method: 'GET',
			headers: { 'Content-Type': 'application/json' },
		});

		if (!response.ok) {
			throw new Error(`HTTP ${response.status}: ${response.statusText}`);
		}

		const data = await response.json();

		// Transform response into store format
		const updatedStatus = {
			radarr: {
				status: data.radarr?.status || 'offline',
				version: data.radarr?.version,
				uptime: data.radarr?.uptime ?? false,
			},
			sonarr: {
				status: data.sonarr?.status || 'offline',
				version: data.sonarr?.version,
				uptime: data.sonarr?.uptime ?? false,
			},
			lidarr: {
				status: data.lidarr?.status || 'offline',
				version: data.lidarr?.version,
				uptime: data.lidarr?.uptime ?? false,
			},
			prowlarr: {
				status: data.prowlarr?.status || 'offline',
				version: data.prowlarr?.version,
				uptime: data.prowlarr?.uptime ?? false,
			},
			lastUpdated: new Date(),
			isLoading: false,
		};

		serviceStatusStore.set(updatedStatus);
	} catch (error) {
		console.error('Failed to refresh service health:', error);

		// Mark all services as offline on error
		serviceStatusStore.update((store) => ({
			...store,
			radarr: { ...store.radarr, status: 'offline' },
			sonarr: { ...store.sonarr, status: 'offline' },
			lidarr: { ...store.lidarr, status: 'offline' },
			prowlarr: { ...store.prowlarr, status: 'offline' },
			lastUpdated: new Date(),
			isLoading: false,
		}));
	}
}

// ============================================================================
// Derived Stores
// ============================================================================

/**
 * System health derived store.
 *
 * Returns true only if all essential services (Radarr and at least one of Sonarr/Lidarr)
 * report an "online" status. Returns false otherwise.
 *
 * @type {import('svelte/store').Readable<boolean>}
 */
export const isSystemHealthy = derived(serviceStatusStore, ($store) => {
	const radarrOnline = $store.radarr?.status === 'online';
	const atLeastOneOnline =
		$store.sonarr?.status === 'online' ||
		$store.lidarr?.status === 'online' ||
		$store.prowlarr?.status === 'online';

	// System is healthy if Radarr (primary service) and at least one other is online
	return radarrOnline && atLeastOneOnline;
});

/**
 * Service count derived store.
 *
 * Returns the number of services currently online.
 *
 * @type {import('svelte/store').Readable<number>}
 */
export const onlineServiceCount = derived(serviceStatusStore, ($store) => {
	const services = ['radarr', 'sonarr', 'lidarr', 'prowlarr'];
	return services.filter((service) => $store[service]?.status === 'online').length;
});

/**
 * Is loading derived store.
 *
 * Returns true if currently fetching service status.
 *
 * @type {import('svelte/store').Readable<boolean>}
 */
export const isHealthLoading = derived(
	serviceStatusStore,
	($store) => $store.isLoading === true,
);

// ============================================================================
// Polling Management
// ============================================================================

let pollingInterval = null;
let isPollingActive = false;

/**
 * Start automatic polling of service health.
 *
 * Polls every 30 seconds (or configured interval).
 * Safe to call multiple times - only one interval is active at a time.
 *
 * @returns {void}
 */
export function startPolling() {
	if (isPollingActive) {
		console.warn('Polling already active');
		return;
	}

	isPollingActive = true;

	// Initial refresh
	refreshHealth();

	// Set up recurring polling
	pollingInterval = setInterval(refreshHealth, POLL_INTERVAL);
	console.log(`Polling started (interval: ${POLL_INTERVAL}ms)`);
}

/**
 * Stop automatic polling of service health.
 *
 * Safe to call even if polling is not active.
 *
 * @returns {void}
 */
export function stopPolling() {
	if (pollingInterval) {
		clearInterval(pollingInterval);
		pollingInterval = null;
	}

	isPollingActive = false;
	console.log('Polling stopped');
}

/**
 * Get the current polling status.
 *
 * @returns {boolean} True if polling is currently active
 */
export function isPolling() {
	return isPollingActive;
}

/**
 * Reset polling (stop and restart).
 *
 * Useful for restarting polling after a configuration change.
 *
 * @returns {void}
 */
export function resetPolling() {
	stopPolling();
	startPolling();
}

// ============================================================================
// User Notification Store
// ============================================================================

/**
 * User notifications store.
 *
 * Stores global notifications/alerts to display in the UI.
 * Items are automatically removed after a timeout.
 *
 * @type {import('svelte/store').Writable<Array<{
 *   id: string,
 *   type: 'info' | 'warning' | 'error' | 'success',
 *   message: string,
 *   timeout?: number
 * }>>}
 */
export const notificationsStore = writable([]);

/**
 * Add a notification.
 *
 * @param {string} message - Notification message
 * @param {'info' | 'warning' | 'error' | 'success'} type - Notification type
 * @param {number} timeout - Auto-dismiss after (ms), or 0 for manual dismiss
 */
export function addNotification(message, type = 'info', timeout = 5000) {
	const id = `notif_${Date.now()}_${Math.random()}`;

	notificationsStore.update((notifications) => [
		...notifications,
		{ id, type, message, timeout },
	]);

	// Auto-dismiss if timeout is set
	if (timeout > 0) {
		setTimeout(() => {
			removeNotification(id);
		}, timeout);
	}
}

/**
 * Remove a notification by ID.
 *
 * @param {string} id - Notification ID
 */
export function removeNotification(id) {
	notificationsStore.update((notifications) =>
		notifications.filter((n) => n.id !== id),
	);
}

/**
 * Clear all notifications.
 */
export function clearNotifications() {
	notificationsStore.set([]);
}

// ============================================================================
// Debug Utilities (Dev Only)
// ============================================================================

/**
 * Log current app state (for debugging).
 *
 * Only logs if DEBUG is enabled.
 */
export function debugAppState() {
	if (typeof window === 'undefined' || !window.DEBUG_ORCHESTRATORR) {
		return;
	}

	console.group('🐛 Orchestratorr App State');

	configStore.subscribe((config) => {
		console.log('Config:', config);
	});

	serviceStatusStore.subscribe((status) => {
		console.log('Service Status:', status);
	});

	console.groupEnd();
}

/**
 * Enable debug mode.
 *
 * Set window.DEBUG_ORCHESTRATORR = true to enable debug logging.
 */
if (typeof window !== 'undefined') {
	window.DEBUG_ORCHESTRATORR = false;
}
