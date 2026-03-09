<!--
Recent Activity Feed Component

Displays the last 5 items grabbed or imported across all services.
Shows appropriate icons based on service type (Movies for Radarr, TV for Sonarr, etc.).
-->

<script>
	/**
	 * Array of recent activities
	 * @type {Array<{ id: string, type: 'movie' | 'tv' | 'music' | 'search', title: string, service: string, timestamp: Date }>}
	 */
	export let activities = [];

	/**
	 * Get icon for activity type
	 */
	function getActivityIcon(type) {
		const icons = {
			movie: '🎬',
			tv: '📺',
			music: '🎵',
			search: '🔍',
			import: '📥',
			download: '📥',
		};
		return icons[type] || '📦';
	}

	/**
	 * Format timestamp
	 */
	function formatTime(date) {
		if (!date) return '';
		const now = new Date();
		const seconds = Math.floor((now - new Date(date)) / 1000);

		if (seconds < 60) return `${seconds}s`;
		if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
		if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
		return new Date(date).toLocaleDateString();
	}

	/**
	 * Get service label
	 */
	function getServiceLabel(service) {
		return (service || 'Unknown').charAt(0).toUpperCase() + service.slice(1);
	}
</script>

<div class="bg-gray-800 border border-gray-700 rounded-lg p-6 shadow-md">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-lg font-semibold text-white">Recent Activity</h2>
		<span class="text-xs text-gray-400">Last 5</span>
	</div>

	{#if activities.length === 0}
		<div class="text-center py-8">
			<p class="text-gray-500">No recent activity</p>
		</div>
	{:else}
		<div class="space-y-3">
			{#each activities.slice(0, 5) as activity (activity.id)}
				<div class="flex items-start gap-3 pb-3 border-b border-gray-700 last:border-b-0">
					<span class="text-xl flex-shrink-0">{getActivityIcon(activity.type)}</span>
					<div class="flex-1 min-w-0">
						<p class="text-sm text-gray-200 truncate">{activity.title}</p>
						<div class="flex items-center gap-2 mt-1">
							<span class="text-xs text-gray-500">
								{getServiceLabel(activity.service)}
							</span>
							<span class="text-xs text-gray-600">
								{formatTime(activity.timestamp)}
							</span>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	/* All styling via Tailwind */
</style>
