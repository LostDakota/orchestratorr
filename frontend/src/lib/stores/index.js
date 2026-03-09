/**
 * Svelte stores for orchestratorr frontend.
 *
 * Re-exports all available stores for convenient importing.
 */

// Status Store (legacy - can be deprecated in favor of serviceStatusStore)
export { statusStore, isAnyServiceDown, initializeStatusPolling, refreshStatus } from './statusStore.js';

// App Store (new - primary state management)
export {
	configStore,
	serviceStatusStore,
	notificationsStore,
	isSystemHealthy,
	onlineServiceCount,
	isHealthLoading,
	getBackendUrl,
	setBackendUrl,
	resetConfig,
	refreshHealth,
	startPolling,
	stopPolling,
	isPolling,
	resetPolling,
	addNotification,
	removeNotification,
	clearNotifications,
	debugAppState,
} from './appStore.js';
