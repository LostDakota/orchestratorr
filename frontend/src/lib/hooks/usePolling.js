/**
 * usePolling hook for Svelte components.
 *
 * Manages the polling lifecycle: starts polling on component mount.
 * Polling continues globally and is not stopped on unmount (can be shared
 * across multiple components).
 *
 * Usage in a component:
 * ```svelte
 * <script>
 *   import { onMount } from 'svelte';
 *   import { usePolling } from '$lib/hooks/usePolling';
 *
 *   onMount(() => {
 *     usePolling();
 *   });
 * </script>
 * ```
 *
 * Or use directly in component:
 * ```svelte
 * <script>
 *   import { startPolling } from '$lib/stores';
 *   import { onMount } from 'svelte';
 *
 *   onMount(startPolling);
 * </script>
 * ```
 */

import { onMount } from 'svelte';
import { isPolling, startPolling } from '../stores/appStore';

/**
 * Initialize polling for the component lifecycle.
 *
 * Automatically starts polling on mount if not already active.
 * Safe to call multiple times - only one polling interval is active at a time.
 *
 * Note: Polling is global and continues even after components unmount.
 * Call stopPolling() directly if you need to stop polling.
 *
 * @returns {void}
 */
export function usePolling() {
	onMount(() => {
		// Check if polling is already active before starting
		// Note: isPolling() returns the current state, not a store
		if (!isPolling()) {
			startPolling();
		}
	});
}
