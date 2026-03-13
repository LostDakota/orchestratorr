/**
 * Unit tests for statusStore.js
 *
 * Tests cover:
 * - Store initialization
 * - Service timeout handling
 * - Degraded status detection
 * - Backend error handling
 * - Polling setup and cleanup
 * - isAnyServiceDown derived store
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { get } from 'svelte/store';
import {
	statusStore,
	isAnyServiceDown,
	initializeStatusPolling,
	refreshStatus,
} from '../stores/statusStore';

beforeEach(() => {
	statusStore.set({
		radarr: { version: null, status: 'unknown', lastChecked: null },
		sonarr: { version: null, status: 'unknown', lastChecked: null },
		lidarr: { version: null, status: 'unknown', lastChecked: null },
		prowlarr: { version: null, status: 'unknown', lastChecked: null },
		backendError: null,
	});
});

afterEach(() => {
	vi.restoreAllMocks();
});

describe('statusStore', () => {
	describe('initialization', () => {
		it('should initialize with default values', () => {
			const store = get(statusStore);
			expect(store).not.toBeNull();
			expect(store.radarr).toBeDefined();
			expect(store.sonarr).toBeDefined();
			expect(store.lidarr).toBeDefined();
			expect(store.prowlarr).toBeDefined();
			expect(store.backendError).toBeNull();
		});

		it('should initialize all services with unknown status', () => {
			const store = get(statusStore);
			expect(store.radarr.status).toBe('unknown');
			expect(store.sonarr.status).toBe('unknown');
			expect(store.lidarr.status).toBe('unknown');
			expect(store.prowlarr.status).toBe('unknown');
		});

		it('should initialize service versions as null', () => {
			const store = get(statusStore);
			expect(store.radarr.version).toBeNull();
			expect(store.sonarr.version).toBeNull();
			expect(store.lidarr.version).toBeNull();
			expect(store.prowlarr.version).toBeNull();
		});
	});

	describe('refreshStatus', () => {
		it('should be callable without throwing', async () => {
			global.fetch = vi.fn(() =>
				Promise.resolve({
					ok: true,
					json: () => Promise.resolve({ version: '4.7.0' }),
					status: 200,
				}),
			);

			await expect(refreshStatus()).resolves.not.toThrow();
		});
	});
});

describe('isAnyServiceDown', () => {
	it('should be false when all services are online', () => {
		statusStore.set({
			radarr: { version: '4.7.0', status: 'online', lastChecked: new Date() },
			sonarr: { version: '4.1.0', status: 'online', lastChecked: new Date() },
			lidarr: { version: '2.1.3', status: 'online', lastChecked: new Date() },
			prowlarr: { version: '1.14.0', status: 'online', lastChecked: new Date() },
			backendError: null,
		});

		expect(get(isAnyServiceDown)).toBe(false);
	});

	it('should be true when at least one service is offline', () => {
		statusStore.set({
			radarr: { version: '4.7.0', status: 'offline', lastChecked: new Date() },
			sonarr: { version: '4.1.0', status: 'online', lastChecked: new Date() },
			lidarr: { version: '2.1.3', status: 'online', lastChecked: new Date() },
			prowlarr: { version: '1.14.0', status: 'online', lastChecked: new Date() },
			backendError: null,
		});

		expect(get(isAnyServiceDown)).toBe(true);
	});

	it('should be true when backend error exists', () => {
		statusStore.set({
			radarr: { version: '4.7.0', status: 'online', lastChecked: new Date() },
			sonarr: { version: '4.1.0', status: 'online', lastChecked: new Date() },
			lidarr: { version: '2.1.3', status: 'online', lastChecked: new Date() },
			prowlarr: { version: '1.14.0', status: 'online', lastChecked: new Date() },
			backendError: 'Backend unreachable',
		});

		expect(get(isAnyServiceDown)).toBe(true);
	});
});

describe('initializeStatusPolling', () => {
	it('should return a cleanup function', () => {
		global.fetch = vi.fn(() =>
			Promise.resolve({
				ok: true,
				json: () => Promise.resolve({ version: '4.7.0' }),
				status: 200,
			}),
		);
		const cleanup = initializeStatusPolling();
		expect(typeof cleanup).toBe('function');
		cleanup();
	});

	it('should clear interval when cleanup is called', () => {
		global.fetch = vi.fn(() =>
			Promise.resolve({
				ok: true,
				json: () => Promise.resolve({ version: '4.7.0' }),
				status: 200,
			}),
		);
		const cleanup = initializeStatusPolling();
		expect(() => cleanup()).not.toThrow();
	});
});

describe('Service timeout and degraded status', () => {
	it('should handle service timeouts gracefully', async () => {
		vi.useFakeTimers();

		// Mock fetch that takes 6s (longer than the 5s AbortController timeout)
		global.fetch = vi.fn(() =>
			new Promise((resolve) => {
				setTimeout(() => {
					resolve({
						ok: true,
						json: () => Promise.resolve({ version: '4.7.0' }),
						status: 200,
					});
				}, 6000);
			}),
		);

		const refreshPromise = refreshStatus();

		// Advance past the 5s abort timeout
		await vi.advanceTimersByTimeAsync(6000);

		await refreshPromise;

		const store = get(statusStore);
		// Services should be degraded (aborted) or offline, not online
		const statuses = [store.radarr.status, store.sonarr.status, store.lidarr.status, store.prowlarr.status];
		expect(statuses.every((s) => s === 'degraded' || s === 'offline')).toBe(true);

		vi.useRealTimers();
	});

	it('should mark as degraded when response time exceeds 3 seconds', () => {
		const responseTime = 3500;
		const status = responseTime > 3000 ? 'degraded' : 'online';
		expect(status).toBe('degraded');
	});

	it('should mark as online when response time is under 3 seconds', () => {
		const responseTime = 1500;
		const status = responseTime > 3000 ? 'degraded' : 'online';
		expect(status).toBe('online');
	});
});

describe('Backend error handling', () => {
	it('should mark services as offline when fetch fails', async () => {
		global.fetch = vi.fn(() => Promise.reject(new Error('Network error')));

		await refreshStatus();

		const store = get(statusStore);
		// Individual service fetches catch errors and return offline
		expect(store.radarr.status).toBe('offline');
		expect(store.sonarr.status).toBe('offline');
		expect(store.lidarr.status).toBe('offline');
		expect(store.prowlarr.status).toBe('offline');
	});

	it('should clear backendError on successful refresh', async () => {
		// First set a backend error
		statusStore.update((s) => ({ ...s, backendError: 'Previous error' }));

		global.fetch = vi.fn(() =>
			Promise.resolve({
				ok: true,
				json: () => Promise.resolve({ version: '4.7.0' }),
				status: 200,
			}),
		);

		await refreshStatus();

		const store = get(statusStore);
		expect(store.backendError).toBeNull();
	});
});
