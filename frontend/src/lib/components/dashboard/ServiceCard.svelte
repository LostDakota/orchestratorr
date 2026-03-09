<!--
Service Card Component

Displays the status of a connected *arr service with version,
last seen timestamp, and quick-link to service UI.
-->

<script>
	import StatusBadge from '../StatusBadge.svelte';

	/**
	 * Service name (e.g., "Radarr", "Sonarr")
	 * @type {string}
	 */
	export let serviceName = '';

	/**
	 * Service status (e.g., "online", "offline", "degraded")
	 * @type {string}
	 */
	export let status = 'unknown';

	/**
	 * Service version string
	 * @type {string}
	 */
	export let version = 'N/A';

	/**
	 * Last seen timestamp
	 * @type {Date | null}
	 */
	export let lastSeen = null;

	/**
	 * Base URL for the service (e.g., http://localhost:7878 for Radarr)
	 * @type {string}
	 */
	export let serviceUrl = '';

	/**
	 * Format timestamp relative to now
	 */
	function formatLastSeen(date) {
		if (!date) return 'Never';
		const now = new Date();
		const seconds = Math.floor((now - new Date(date)) / 1000);

		if (seconds < 60) return `${seconds}s ago`;
		if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
		if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
		return new Date(date).toLocaleDateString();
	}

	/**
	 * Get service icon emoji
	 */
	function getServiceIcon(name) {
		const icons = {
			radarr: '🎬',
			sonarr: '📺',
			lidarr: '🎵',
			prowlarr: '🔍',
		};
		return icons[name.toLowerCase()] || '📦';
	}
</script>

<div
	class="bg-gray-800 border border-gray-700 rounded-lg p-6 shadow-md hover:shadow-lg hover:border-gray-600 transition-all duration-200"
>
	<!-- Header -->
	<div class="flex items-start justify-between mb-4">
		<div class="flex items-center gap-3">
			<span class="text-3xl">{getServiceIcon(serviceName)}</span>
			<div>
				<h3 class="text-lg font-semibold text-white">{serviceName}</h3>
				<p class="text-xs text-gray-400">Media Service</p>
			</div>
		</div>
	</div>

	<!-- Status Badge -->
	<div class="mb-4">
		<StatusBadge {status} />
	</div>

	<!-- Info Grid -->
	<div class="space-y-2 mb-4 text-sm">
		<div class="flex justify-between">
			<span class="text-gray-400">Version</span>
			<span class="text-gray-200 font-mono">{version}</span>
		</div>
		<div class="flex justify-between">
			<span class="text-gray-400">Last Seen</span>
			<span class="text-gray-200">{formatLastSeen(lastSeen)}</span>
		</div>
	</div>

	<!-- Quick Link Button -->
	{#if serviceUrl}
		<a
			href={serviceUrl}
			target="_blank"
			rel="noopener noreferrer"
			class="block w-full text-center py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200"
		>
			Open UI →
		</a>
	{/if}
</div>

<style>
	/* No additional styles needed - all Tailwind */
</style>
