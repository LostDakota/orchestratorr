<!--
Main application entry point for Orchestratorr.

Displays the real-time service status dashboard.
-->

<script>
	import StatusGrid from './lib/components/StatusGrid.svelte';
</script>

<StatusGrid />

<style>
	:global(body, html) {
		margin: 0;
		padding: 0;
		background-color: #111827;
		color: #f3f4f6;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue',
			Arial, sans-serif;
	}

	:global(*) {
		box-sizing: border-box;
	}
</style>
