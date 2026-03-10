<script>
	import { redirect } from '@sveltejs/kit';
	import { onMount } from 'svelte';
	
	onMount(() => {
		window.location.href = '/dashboard';
	});
</script>

<svelte:head>
	<title>Redirecting to Dashboard...</title>
</svelte:head>

<div class="p-8 text-center">
	<h1 class="text-2xl font-bold text-white">Orchestratorr</h1>
	<p class="text-gray-400">Redirecting to dashboard...</p>
</div>