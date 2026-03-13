/**
 * Logic tests for StatusGrid behavior.
 *
 * Tests cover:
 * - Store-driven status summary logic
 * - Error banner conditions
 * - Service card data structure
 * - Polling setup and cleanup
 *
 * Note: Svelte 5 component rendering requires @testing-library/svelte.
 * These tests validate the logic/data layer without DOM rendering.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import {
	statusStore,
	isAnyServiceDown,
	initializeStatusPolling,
} from '../stores/statusStore';

function makeStore(overrides = {}) {
	return {
		radarr: { version: null, status: 'unknown', lastChecked: null },
		sonarr: { version: null, status: 'unknown', lastChecked: null },
		lidarr: { version: null, status: 'unknown', lastChecked: null },
		prowlarr: { version: null, status: 'unknown', lastChecked: null },
		backendError: null,
		...overrides,
	};
}

describe('StatusGrid Logic', () => {
	beforeEach(() => {
		statusStore.set(makeStore());
	});

	describe('status summary', () => {
		it('should report all systems operational when all online', () => {
			statusStore.set(makeStore({
				radarr: { version: '4.7.0', status: 'online', lastChecked: new Date() },
				sonarr: { version: '4.1.0', status: 'online', lastChecked: new Date() },
				lidarr: { version: '2.1.3', status: 'online', lastChecked: new Date() },
				prowlarr: { version: '1.14.0', status: 'online', lastChecked: new Date() },
			}));
			expect(get(isAnyServiceDown)).toBe(false);
		});

		it('should report degraded when a service is offline', () => {
			statusStore.set(makeStore({
				radarr: { version: '4.7.0', status: 'offline', lastChecked: new Date() },
				sonarr: { version: '4.1.0', status: 'online', lastChecked: new Date() },
				lidarr: { version: '2.1.3', status: 'online', lastChecked: new Date() },
				prowlarr: { version: '1.14.0', status: 'online', lastChecked: new Date() },
			}));
			expect(get(isAnyServiceDown)).toBe(true);
		});

		it('should report system offline when backendError exists', () => {
			statusStore.set(makeStore({
				backendError: 'Backend unreachable',
			}));
			expect(get(isAnyServiceDown)).toBe(true);
		});

		it('should not report down when backendError is null and all online', () => {
			statusStore.set(makeStore({
				radarr: { version: '4.7.0', status: 'online', lastChecked: new Date() },
				sonarr: { version: '4.1.0', status: 'online', lastChecked: new Date() },
				lidarr: { version: '2.1.3', status: 'online', lastChecked: new Date() },
				prowlarr: { version: '1.14.0', status: 'online', lastChecked: new Date() },
			}));
			expect(get(isAnyServiceDown)).toBe(false);
		});
	});

	describe('store structure', () => {
		it('should have all four services', () => {
			const store = get(statusStore);
			expect(store.radarr).toBeDefined();
			expect(store.sonarr).toBeDefined();
			expect(store.lidarr).toBeDefined();
			expect(store.prowlarr).toBeDefined();
		});

		it('should initialize with unknown status', () => {
			const store = get(statusStore);
			expect(store.radarr.status).toBe('unknown');
			expect(store.sonarr.status).toBe('unknown');
		});

		it('should initialize versions as null', () => {
			const store = get(statusStore);
			expect(store.radarr.version).toBeNull();
			expect(store.sonarr.version).toBeNull();
		});

		it('should initialize backendError as null', () => {
			const store = get(statusStore);
			expect(store.backendError).toBeNull();
		});
	});

	describe('version display', () => {
		it('should store version strings', () => {
			statusStore.set(makeStore({
				radarr: { version: '4.7.0', status: 'online', lastChecked: new Date() },
				sonarr: { version: '4.1.0', status: 'online', lastChecked: new Date() },
			}));
			const store = get(statusStore);
			expect(store.radarr.version).toBe('4.7.0');
			expect(store.sonarr.version).toBe('4.1.0');
		});
	});

	describe('polling', () => {
		it('should return a cleanup function', () => {
			const cleanup = initializeStatusPolling();
			expect(typeof cleanup).toBe('function');
			cleanup();
		});

		it('should not throw on cleanup', () => {
			const cleanup = initializeStatusPolling();
			expect(() => cleanup()).not.toThrow();
		});
	});
});
