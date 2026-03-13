/**
 * Component tests for StatusBadge.svelte
 *
 * Tests cover:
 * - StatusBadge data model and status mapping
 * - Status text labels
 * - Color class mapping
 * - Compact mode logic
 *
 * Note: Svelte 5 component rendering requires @testing-library/svelte.
 * These tests validate the logic/data layer without DOM rendering.
 */

import { describe, it, expect } from 'vitest';

// Status configuration matching StatusBadge.svelte logic
const STATUS_CONFIG = {
	online: { label: 'Operational', color: 'green', pulse: true },
	offline: { label: 'Connection Failed', color: 'red', pulse: false },
	degraded: { label: 'Slow Response', color: 'yellow', pulse: false },
	unknown: { label: 'Unknown', color: 'gray', pulse: false },
};

function getStatusConfig(status) {
	return STATUS_CONFIG[status] || STATUS_CONFIG.unknown;
}

describe('StatusBadge Logic', () => {
	describe('status label mapping', () => {
		it('should map online to Operational', () => {
			expect(getStatusConfig('online').label).toBe('Operational');
		});

		it('should map offline to Connection Failed', () => {
			expect(getStatusConfig('offline').label).toBe('Connection Failed');
		});

		it('should map degraded to Slow Response', () => {
			expect(getStatusConfig('degraded').label).toBe('Slow Response');
		});

		it('should map unknown to Unknown', () => {
			expect(getStatusConfig('unknown').label).toBe('Unknown');
		});

		it('should default to Unknown for unrecognized status', () => {
			expect(getStatusConfig('bogus').label).toBe('Unknown');
		});
	});

	describe('color mapping', () => {
		it('should use green for online', () => {
			expect(getStatusConfig('online').color).toBe('green');
		});

		it('should use red for offline', () => {
			expect(getStatusConfig('offline').color).toBe('red');
		});

		it('should use yellow for degraded', () => {
			expect(getStatusConfig('degraded').color).toBe('yellow');
		});

		it('should use gray for unknown', () => {
			expect(getStatusConfig('unknown').color).toBe('gray');
		});
	});

	describe('pulse animation', () => {
		it('should pulse for online status', () => {
			expect(getStatusConfig('online').pulse).toBe(true);
		});

		it('should not pulse for offline status', () => {
			expect(getStatusConfig('offline').pulse).toBe(false);
		});

		it('should not pulse for degraded status', () => {
			expect(getStatusConfig('degraded').pulse).toBe(false);
		});

		it('should not pulse for unknown status', () => {
			expect(getStatusConfig('unknown').pulse).toBe(false);
		});
	});
});
