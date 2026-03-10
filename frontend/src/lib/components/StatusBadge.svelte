<!--
Status Badge Component

Displays a visual indicator of service status with a colored dot and status text.
Supports three states: online (green, pulsing), offline (red, static), and degraded (yellow, static).
-->

<script>
	/**
	 * Status value: 'online', 'offline', 'degraded', or 'unknown'
	 * @type {string}
	 */
	export let status = 'unknown';

	/**
	 * Compact mode - smaller sizing for inline display
	 * @type {boolean}
	 */
	export let compact = false;

	// Map status to color and text
	const statusConfig = {
		online: {
			dot: 'bg-green-500',
			text: 'Operational',
			pulse: true,
			bgColor: 'bg-green-50 dark:bg-green-950',
			textColor: 'text-green-700 dark:text-green-200',
		},
		offline: {
			dot: 'bg-red-500',
			text: 'Connection Failed',
			pulse: false,
			bgColor: 'bg-red-50 dark:bg-red-950',
			textColor: 'text-red-700 dark:text-red-200',
		},
		degraded: {
			dot: 'bg-yellow-500',
			text: 'Slow Response',
			pulse: false,
			bgColor: 'bg-yellow-50 dark:bg-yellow-950',
			textColor: 'text-yellow-700 dark:text-yellow-200',
		},
		unknown: {
			dot: 'bg-gray-400',
			text: 'Unknown',
			pulse: false,
			bgColor: 'bg-gray-50 dark:bg-gray-900',
			textColor: 'text-gray-700 dark:text-gray-300',
		},
	};

	// @ts-ignore
	$: config = statusConfig[status] || statusConfig.unknown;
</script>

<div class={compact ? 'inline-flex items-center gap-1.5' : 'flex items-center gap-2'}>
	<!-- Status Dot -->
	<div class="relative {compact ? 'w-2 h-2' : 'w-3 h-3'}">
		<div
			class="absolute inset-0 rounded-full {config.dot} {config.pulse
				? 'animate-pulse'
				: ''}"
		></div>
		{#if config.pulse}
			<div
				class="absolute inset-0 rounded-full {config.dot} opacity-75 animate-ping"
			></div>
		{/if}
	</div>

	<!-- Status Text -->
	<span
		class={`font-medium {compact ? 'text-xs' : 'text-sm'} ${config.textColor}`}
	>
		{config.text}
	</span>
</div>

<style>
	/* Custom pulse animation for online status */
	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}

	:global(.animate-pulse) {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	@keyframes ping {
		75%,
		100% {
			transform: scale(2);
			opacity: 0;
		}
	}

	:global(.animate-ping) {
		animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
	}
</style>
