<!--
Disk Space Overview Component

Displays remaining disk space on root media drives as a horizontal progress bar.
Shows available vs total space with percentage.
-->

<script>
	/**
	 * Total disk space in GB
	 * @type {number}
	 */
	export let total = 0;

	/**
	 * Used disk space in GB
	 * @type {number}
	 */
	export let used = 0;

	/**
	 * Remaining disk space in GB
	 * @type {number}
	 */
	export let available = 0;

	/**
	 * Root folder path
	 * @type {string}
	 */
	export let path = '/media';

	/**
	 * Calculate percentage used
	 */
	$: percentageUsed = total > 0 ? Math.round((used / total) * 100) : 0;
	$: percentageAvailable = 100 - percentageUsed;

	/**
	 * Determine status color based on usage
	 */
	$: statusColor =
		percentageUsed > 90
			? 'bg-red-600'
			: percentageUsed > 75
				? 'bg-yellow-600'
				: 'bg-green-600';

	/**
	 * Format bytes to GB/TB
	 */
	function formatSize(gb) {
		if (gb >= 1024) {
			return (gb / 1024).toFixed(2) + ' TB';
		}
		return gb.toFixed(2) + ' GB';
	}
</script>

<div class="bg-gray-800 border border-gray-700 rounded-lg p-6 shadow-md">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-lg font-semibold text-white">Disk Space</h2>
		<span class="text-2xl font-bold {statusColor === 'bg-red-600' ? 'text-red-400' : statusColor === 'bg-yellow-600' ? 'text-yellow-400' : 'text-green-400'}">
			{percentageUsed}%
		</span>
	</div>

	<!-- Path Info -->
	<p class="text-sm text-gray-400 mb-4 font-mono">{path}</p>

	<!-- Progress Bar -->
	<div class="mb-4">
		<div class="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
			<div
				class="{statusColor} h-full rounded-full transition-all duration-300"
				style="width: {percentageUsed}%"
			></div>
		</div>
	</div>

	<!-- Stats Grid -->
	<div class="grid grid-cols-3 gap-2 text-sm">
		<div class="bg-gray-900 rounded p-3">
			<p class="text-gray-500 text-xs uppercase mb-1">Used</p>
			<p class="text-white font-semibold">{formatSize(used)}</p>
		</div>
		<div class="bg-gray-900 rounded p-3">
			<p class="text-gray-500 text-xs uppercase mb-1">Available</p>
			<p class="text-white font-semibold">{formatSize(available)}</p>
		</div>
		<div class="bg-gray-900 rounded p-3">
			<p class="text-gray-500 text-xs uppercase mb-1">Total</p>
			<p class="text-white font-semibold">{formatSize(total)}</p>
		</div>
	</div>

	<!-- Warning -->
	{#if percentageUsed > 90}
		<div class="mt-4 bg-red-900/20 border border-red-700/30 rounded p-3">
			<p class="text-sm text-red-200">⚠️ Disk usage critical (>90%)</p>
		</div>
	{:else if percentageUsed > 75}
		<div class="mt-4 bg-yellow-900/20 border border-yellow-700/30 rounded p-3">
			<p class="text-sm text-yellow-200">⚠️ Disk usage high (>75%)</p>
		</div>
	{/if}
</div>

<style>
	/* All styling via Tailwind */
</style>
