<script>
	import { onMount } from 'svelte';
	import { Search, X, Loader2, Film, Tv } from 'lucide-svelte';
	import { getBackendUrl } from '../stores/appStore.js';

	let searchQuery = '';
	let results = [];
	let loading = false;
	let showResults = false;
	let error = null;
	let debounceTimer = null;

	// Debounce delay in milliseconds
	const DEBOUNCE_MS = 300;

	/**
	 * Debounce helper: delays function execution until user stops typing
	 */
	function debounceSearch(query) {
		if (debounceTimer) clearTimeout(debounceTimer);

		if (!query || query.trim().length < 2) {
			results = [];
			showResults = false;
			return;
		}

		loading = true;
		debounceTimer = setTimeout(() => {
			performSearch(query);
		}, DEBOUNCE_MS);
	}

	/**
	 * Execute the search API call
	 */
	async function performSearch(query) {
		try {
			error = null;
			const backendUrl = getBackendUrl();
			const encodedQuery = encodeURIComponent(query);
			const response = await fetch(`${backendUrl}/api/v1/search?q=${encodedQuery}&limit=10`);

			if (!response.ok) {
				throw new Error(`Search failed: ${response.statusText}`);
			}

			const data = await response.json();
			results = data.results || [];
			showResults = true;
		} catch (err) {
			console.error('Search error:', err);
			error = err.message;
			results = [];
		} finally {
			loading = false;
		}
	}

	/**
	 * Handle input change
	 */
	function handleInput(e) {
		searchQuery = e.target.value;
		debounceSearch(searchQuery);
	}

	/**
	 * Clear search
	 */
	function clearSearch() {
		searchQuery = '';
		results = [];
		showResults = false;
		error = null;
		if (debounceTimer) clearTimeout(debounceTimer);
	}

	/**
	 * Close results dropdown
	 */
	function closeResults() {
		showResults = false;
	}

	/**
	 * Handle result selection (placeholder for now)
	 */
	function selectResult(result) {
		console.log('Selected result:', result);
		// TODO: Implement add-to-library functionality
		closeResults();
	}

	// Close dropdown when clicking outside
	function handleClickOutside(e) {
		if (showResults && !e.target.closest('.search-container')) {
			closeResults();
		}
	}

	onMount(() => {
		document.addEventListener('click', handleClickOutside);
		return () => document.removeEventListener('click', handleClickOutside);
	});
</script>

<div class="search-container relative w-full max-w-2xl mx-auto">
	<!-- Search Input -->
	<div
		class="relative flex items-center gap-3 px-4 py-3 rounded-lg
               bg-gradient-to-r from-slate-800 to-slate-900
               border border-slate-700 shadow-lg
               hover:border-slate-600 transition-colors"
	>
		<Search size={20} class="text-slate-400" />
		<input
			type="text"
			placeholder="Search movies, TV shows, and music..."
			value={searchQuery}
			on:input={handleInput}
			on:focus={() => {
				if (results.length > 0) showResults = true;
			}}
			class="flex-1 bg-transparent text-white placeholder-slate-500
                   focus:outline-none font-medium"
		/>
		{#if loading}
			<Loader2 size={20} class="text-blue-400 animate-spin" />
		{:else if searchQuery}
			<button
				on:click={clearSearch}
				class="text-slate-400 hover:text-white transition-colors"
				aria-label="Clear search"
			>
				<X size={20} />
			</button>
		{/if}
	</div>

	<!-- Results Dropdown -->
	{#if showResults && (results.length > 0 || error)}
		<div
			class="absolute top-full left-0 right-0 mt-2 rounded-lg
                   bg-slate-900 border border-slate-700 shadow-2xl z-50"
		>
			{#if error}
				<div class="px-4 py-3 text-red-400 text-sm">{error}</div>
			{:else if results.length > 0}
				<div class="max-h-96 overflow-y-auto">
					{#each results as result (result.tmdb_id || result.title)}
						<button
							on:click={() => selectResult(result)}
							class="w-full px-4 py-3 flex items-start gap-3 border-b border-slate-700
                                   hover:bg-slate-800 transition-colors text-left last:border-b-0"
						>
							<!-- Poster Thumbnail -->
							{#if result.poster_url}
								<img
									src={result.poster_url}
									alt={result.title}
									class="w-10 h-16 object-cover rounded flex-shrink-0"
								/>
							{:else}
								<div
									class="w-10 h-16 bg-slate-700 rounded flex items-center justify-center
                                       flex-shrink-0"
								>
									{#if result.source_type === 'movie'}
										<Film size={20} class="text-slate-500" />
									{:else}
										<Tv size={20} class="text-slate-500" />
									{/if}
								</div>
							{/if}

							<!-- Result Info -->
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-2">
									<p class="font-semibold text-white truncate">{result.title}</p>
									{#if result.year}
										<span class="text-slate-400 text-sm">{result.year}</span>
									{/if}
								</div>

								<!-- Type Badge -->
								<div class="flex items-center gap-2 mt-1">
									<span
										class={`inline-flex px-2 py-1 rounded text-xs font-medium
                                       ${
											result.source_type === 'movie'
												? 'bg-blue-900 text-blue-200'
												: 'bg-purple-900 text-purple-200'
										}`}
									>
										{result.source_type === 'movie' ? '🎬 Movie' : '📺 TV'}
									</span>
									<span class="text-slate-500 text-xs capitalize">
										{result.source_service}
									</span>
								</div>

								<!-- Status -->
								{#if result.in_library}
									<p class="text-green-400 text-xs mt-1">✓ In Library</p>
								{:else}
									<p class="text-yellow-400 text-xs mt-1">+ Add to Library</p>
								{/if}
							</div>
						</button>
					{/each}
				</div>
			{:else}
				<div class="px-4 py-3 text-slate-400 text-sm">No results found</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	:global(.animate-spin) {
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}
</style>
