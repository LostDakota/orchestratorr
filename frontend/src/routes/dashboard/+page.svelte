<!--
Main Dashboard Page

Primary landing page that aggregates all service status, activity, and disk space information.
Responsive grid layout that adapts from desktop (3 col) to mobile (1 col).
-->

<script>
	import { onMount } from 'svelte';
	import ServiceCard from '$lib/components/dashboard/ServiceCard.svelte';
	import RecentActivity from '$lib/components/dashboard/RecentActivity.svelte';
	import DiskSpace from '$lib/components/dashboard/DiskSpace.svelte';
	import SettingsPanel from '$lib/components/SettingsPanel.svelte';

	import {
		serviceStatusStore,
		isSystemHealthy,
		onlineServiceCount,
		isHealthLoading,
		refreshHealth,
		startPolling,
		stopPolling,
	} from '$lib/stores/appStore';

	// Mock data for recent activities (will be replaced with real data from API)
	let recentActivities = [
		{
			id: '1',
			type: 'movie',
			title: 'The Matrix',
			service: 'radarr',
			timestamp: new Date(Date.now() - 5 * 60000),
		},
		{
			id: '2',
			type: 'tv',
			title: 'Breaking Bad S01E01',
			service: 'sonarr',
			timestamp: new Date(Date.now() - 15 * 60000),
		},
		{
			id: '3',
			type: 'movie',
			title: 'Inception',
			service: 'radarr',
			timestamp: new Date(Date.now() - 30 * 60000),
		},
		{
			id: '4',
			type: 'music',
			title: 'Pink Floyd - The Wall',
			service: 'lidarr',
			timestamp: new Date(Date.now() - 1 * 3600000),
		},
		{
			id: '5',
			type: 'search',
			title: 'Found 3 new releases',
			service: 'radarr',
			timestamp: new Date(Date.now() - 2 * 3600000),
		},
	];

	// Mock disk space data (will be replaced with real data from API)
	let diskSpace = {
		path: '/media',
		total: 4000,
		used: 2800,
		available: 1200,
	};

	// Service configurations
	const services = [
		{
			name: 'Radarr',
			url: 'http://localhost:7878',
			key: 'radarr',
		},
		{
			name: 'Sonarr',
			url: 'http://localhost:8989',
			key: 'sonarr',
		},
		{
			name: 'Lidarr',
			url: 'http://localhost:8686',
			key: 'lidarr',
		},
		{
			name: 'Prowlarr',
			url: 'http://localhost:9696',
			key: 'prowlarr',
		},
	];

	onMount(() => {
		// Start polling on mount
		startPolling();

		// Cleanup on unmount
		return () => {
			// Don't stop polling as it's global
		};
	});

	/**
	 * Handle manual refresh
	 */
	async function handleRefresh() {
		await refreshHealth();
	}

	/**
	 * Get status summary text
	 */
	function getStatusSummary() {
		if (!$isSystemHealthy) {
			return 'System Degraded';
		}
		return `${$onlineServiceCount}/4 Services Online`;
	}

	/**
	 * Get status color
	 */
	function getStatusColor() {
		if (!$isSystemHealthy) {
			return 'text-yellow-400';
		}
		return 'text-green-400';
	}
</script>

<svelte:head>
	<title>Dashboard - Orchestratorr</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
	<!-- Header -->
	<header class="border-b border-gray-700 bg-gray-800/50 backdrop-blur-sm sticky top-0 z-40">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<div class="flex items-center justify-between">
				<div>
					<h1 class="text-3xl font-bold text-white">Orchestratorr</h1>
					<p class="text-gray-400 text-sm mt-1">Unified Media Management Dashboard</p>
				</div>
				<div class="flex items-center gap-3">
					<div class="text-right">
						<p class={`text-lg font-semibold ${getStatusColor()}`}>
							{getStatusSummary()}
						</p>
						<p class="text-xs text-gray-500">
							{#if $serviceStatusStore.lastUpdated}
								Updated {new Date($serviceStatusStore.lastUpdated).toLocaleTimeString()}
							{:else}
								Initializing...
							{/if}
						</p>
					</div>
					<button
						on:click={handleRefresh}
						disabled={$isHealthLoading}
						class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
					>
						<span class={$isHealthLoading ? 'animate-spin' : ''}>🔄</span>
						{$isHealthLoading ? 'Refreshing...' : 'Refresh All'}
					</button>
					<SettingsPanel />
				</div>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Service Cards Grid -->
		<section class="mb-8">
			<h2 class="text-2xl font-bold text-white mb-4">Service Status</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				{#each services as service (service.key)}
					<ServiceCard
						serviceName={service.name}
						status={$serviceStatusStore[service.key]?.status || 'unknown'}
						version={$serviceStatusStore[service.key]?.version || 'N/A'}
						lastSeen={$serviceStatusStore[service.key]?.lastChecked}
						serviceUrl={service.url}
					/>
				{/each}
			</div>
		</section>

		<!-- Activity and Disk Space -->
		<section class="grid grid-cols-1 lg:grid-cols-3 gap-4">
			<!-- Recent Activity (takes up 2 columns on desktop) -->
			<div class="lg:col-span-2">
				<RecentActivity activities={recentActivities} />
			</div>

			<!-- Disk Space (takes up 1 column) -->
			<div>
				<DiskSpace {...diskSpace} />
			</div>
		</section>
	</main>

	<!-- Footer -->
	<footer class="border-t border-gray-700 bg-gray-800/50 mt-12">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<p class="text-gray-500 text-sm text-center">
				Orchestratorr • Unified *arr Frontend • Auto-refresh every 30 seconds
			</p>
		</div>
	</footer>
</div>

<style>
	/* Animations */
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	:global(.animate-spin) {
		animation: spin 1s linear infinite;
	}
</style>
