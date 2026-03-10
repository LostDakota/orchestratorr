<!--
Real-time Service Status Dashboard

Displays a grid of service status cards for all configured *arr services.
Auto-refreshes every 30 seconds and shows a global alert if the backend is unreachable.
-->

<script>
	import { onMount, onDestroy } from 'svelte';
	import { statusStore, initializeStatusPolling, refreshStatus, isAnyServiceDown } from '../stores/statusStore';
	import StatusBadge from './StatusBadge.svelte';

	let services = [];
	let isLoading = true;
	let unsubscribePolling;

	const serviceNames = {
		radarr: { label: 'Radarr', icon: '🎬' },
		sonarr: { label: 'Sonarr', icon: '📺' },
		lidarr: { label: 'Lidarr', icon: '🎵' },
		prowlarr: { label: 'Prowlarr', icon: '🔍' },
	};

	/**
	 * Update services array from store
	 */
	function updateServices(store) {
		services = Object.entries(serviceNames).map(([key, meta]) => ({
			id: key,
			label: meta.label,
			icon: meta.icon,
			version: store[key]?.version || 'N/A',
			status: store[key]?.status || 'unknown',
			lastChecked: store[key]?.lastChecked,
		}));
		isLoading = false;
	}

	/**
	 * Format last checked timestamp
	 */
	function formatLastChecked(date) {
		if (!date) return 'Never';
		const now = new Date();
		const diff = Math.floor((now - date) / 1000);

		if (diff < 60) return `${diff}s ago`;
		if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
		return date.toLocaleTimeString();
	}

	/**
	 * Handle manual refresh
	 */
	async function handleRefresh() {
		isLoading = true;
		await refreshStatus();
		isLoading = false;
	}

	// Subscribe to store changes
	const unsubscribeStore = statusStore.subscribe((store) => {
		updateServices(store);
	});

	// Initialize polling on mount
	onMount(() => {
		unsubscribePolling = initializeStatusPolling();
	});

	// Cleanup on unmount
	onDestroy(() => {
		if (unsubscribePolling) {
			unsubscribePolling();
		}
		unsubscribeStore();
	});
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
	<!-- Header -->
	<header class="border-b border-gray-700 bg-gray-800/50 backdrop-blur-sm sticky top-0 z-40">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-2xl font-bold text-white">Service Status Dashboard</h1>
					<p class="text-gray-400 text-sm mt-1">Real-time monitoring of *arr services</p>
				</div>
				<button
					on:click={handleRefresh}
					disabled={isLoading}
					class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
				>
					<span class={isLoading ? 'animate-spin' : ''}>🔄</span>
					{isLoading ? 'Refreshing...' : 'Refresh Now'}
				</button>
			</div>
		</div>
	</header>

	<!-- Global Alert Banner -->
	{#if $statusStore.backendError}
		<div class="bg-red-900/50 border-l-4 border-red-500 p-4 m-4">
			<div class="flex items-start">
				<div class="flex-shrink-0">
					<span class="text-2xl">⚠️</span>
				</div>
				<div class="ml-3">
					<p class="text-sm font-medium text-red-200">Backend Connection Error</p>
					<p class="text-sm text-red-100 mt-1">{$statusStore.backendError}</p>
				</div>
			</div>
		</div>
	{/if}

	<!-- Main Content -->
	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Status Summary -->
		<div class="mb-8">
			<div class="bg-gray-800/30 border border-gray-700 rounded-lg p-4">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-gray-400 text-sm">Overall Status</p>
						<p class="text-white text-lg font-semibold mt-1">
							{#if $statusStore.backendError}
								System Offline
							{:else if $isAnyServiceDown}
								Service Degraded
							{:else}
								All Systems Operational
							{/if}
						</p>
					</div>
					<div class="text-right">
						<p class="text-gray-400 text-sm">Last Updated</p>
						<p class="text-white text-lg font-semibold mt-1">
							{#if services[0]?.lastChecked}
								{formatLastChecked(services[0].lastChecked)}
							{:else}
								—
							{/if}
						</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Service Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			{#each services as service (service.id)}
				<div
					class="bg-gray-800/40 border border-gray-700 rounded-lg p-6 hover:bg-gray-800/60 transition-colors duration-200 {service.status ===
					'offline'
						? 'border-red-700/50'
						: service.status === 'degraded'
							? 'border-yellow-700/50'
							: 'border-green-700/20'}"
				>
					<!-- Service Header -->
					<div class="flex items-start justify-between mb-4">
						<div class="flex items-center gap-2">
							<span class="text-2xl">{service.icon}</span>
							<div>
								<h3 class="text-white font-semibold">{service.label}</h3>
								<p class="text-gray-400 text-xs mt-0.5">Service Monitor</p>
							</div>
						</div>
					</div>

					<!-- Version Information -->
					<div class="mb-4 p-3 bg-gray-900/40 rounded border border-gray-700/50">
						<p class="text-gray-400 text-xs font-medium uppercase tracking-wider">
							Version
						</p>
						<p class="text-white text-sm font-mono mt-1">{service.version}</p>
					</div>

					<!-- Status Badge -->
					<div class="mb-4">
						<p class="text-gray-400 text-xs font-medium uppercase tracking-wider mb-2">
							Status
						</p>
						<StatusBadge status={service.status} />
					</div>

					<!-- Last Checked -->
					<div
						class="pt-3 border-t border-gray-700/50 flex justify-between items-center text-xs"
					>
						<span class="text-gray-500">Last Checked</span>
						<span class="text-gray-400 font-mono">
							{formatLastChecked(service.lastChecked)}
						</span>
					</div>
				</div>
			{/each}
		</div>

		<!-- Auto-refresh Info -->
		<div class="mt-8 text-center text-gray-500 text-sm">
			<p>🔄 Auto-refreshing every 30 seconds</p>
		</div>
	</main>
</div>

<style>
	:global(body) {
		background-color: #111827;
	}
</style>
