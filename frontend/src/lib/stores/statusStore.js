/**
 * Real-time service status store.
 *
 * Polls the FastAPI backend every 30 seconds for system health data
 * from all configured *arr services (Radarr, Sonarr, Lidarr, Prowlarr).
 *
 * Stores the results in a Svelte writable store so any component
 * can subscribe to service status updates.
 */

import { writable, derived } from 'svelte/store';

const POLL_INTERVAL = 30000; // 30 seconds
const getApiBase = () => {
	if (import.meta.env.VITE_API_BASE !== undefined) {
		// If defined (including empty string), use it
		const base = import.meta.env.VITE_API_BASE;
		return base ? base + '/api/v1' : '/api/v1';
	}
	return 'http://localhost:8000/api/v1';
};
const API_BASE = getApiBase(); // FastAPI backend URL

/**
 * Service status store.
 *
 * Structure:
 * {
 *   radarr: { version: '4.7.0', status: 'online'|'offline'|'degraded', lastChecked: Date },
 *   sonarr: { version: '4.1.0', status: 'online'|'offline'|'degraded', lastChecked: Date },
 *   lidarr: { version: '2.1.3', status: 'online'|'offline'|'degraded', lastChecked: Date },
 *   prowlarr: { version: '1.14.0', status: 'online'|'offline'|'degraded', lastChecked: Date },
 *   backendError: null | string // Error message if backend is unreachable
 * }
 */
export const statusStore = writable({
	radarr: { version: null, status: 'unknown', lastChecked: null },
	sonarr: { version: null, status: 'unknown', lastChecked: null },
	lidarr: { version: null, status: 'unknown', lastChecked: null },
	prowlarr: { version: null, status: 'unknown', lastChecked: null },
	backendError: null,
});

/**
 * Derived store that determines if any service is offline.
 */
export const isAnyServiceDown = derived(statusStore, ($store) => {
	if ($store.backendError) return true;
	return Object.values($store)
		.filter((v) => typeof v === 'object' && v !== null && 'status' in v)
		.some((service) => service.status === 'offline');
});

/**
 * Fetch status for a single *arr service.
 * @param {string} service - Service name (radarr, sonarr, lidarr, prowlarr)
 * @returns {Promise<{version: string, status: string, responseTime: number}>}
 */
async function fetchServiceStatus(service) {
	const startTime = performance.now();
	const timeout = 5000; // 5 second timeout per service

	try {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), timeout);

		const response = await fetch(`${API_BASE}/${service}/system/status`, {
			signal: controller.signal,
		});

		clearTimeout(timeoutId);
		const endTime = performance.now();
		const responseTime = endTime - startTime;

		if (!response.ok) {
			return { version: null, status: 'offline', responseTime };
		}

		const data = await response.json();
		const status = responseTime > 3000 ? 'degraded' : 'online';

		return {
			version: data.version || 'Unknown',
			status,
			responseTime,
		};
	} catch (error) {
		if (error.name === 'AbortError') {
			return { version: null, status: 'degraded', responseTime: timeout };
		}
		return { version: null, status: 'offline', responseTime: 0 };
	}
}

/**
 * Poll all services and update the store.
 */
async function pollServices() {
	try {
		// Fetch all services in parallel
		const [radarr, sonarr, lidarr, prowlarr] = await Promise.all([
			fetchServiceStatus('radarr'),
			fetchServiceStatus('sonarr'),
			fetchServiceStatus('lidarr'),
			fetchServiceStatus('prowlarr'),
		]);

		statusStore.update((store) => ({
			...store,
			radarr: { ...radarr, lastChecked: new Date() },
			sonarr: { ...sonarr, lastChecked: new Date() },
			lidarr: { ...lidarr, lastChecked: new Date() },
			prowlarr: { ...prowlarr, lastChecked: new Date() },
			backendError: null, // Clear any previous backend error
		}));
	} catch (error) {
		// If the entire backend is unreachable
		statusStore.update((store) => ({
			...store,
			backendError: 'Backend service unreachable. Check FastAPI server status.',
		}));
	}
}

/**
 * Initialize polling.
 * Start polling immediately and then every POLL_INTERVAL.
 * @returns {function} Unsubscribe function to stop polling
 */
export function initializeStatusPolling() {
	// Initial poll
	pollServices();

	// Set up recurring polling
	const intervalId = setInterval(pollServices, POLL_INTERVAL);

	// Return cleanup function
	return () => clearInterval(intervalId);
}

/**
 * Manual refresh - fetch latest status immediately.
 */
export async function refreshStatus() {
	await pollServices();
}
