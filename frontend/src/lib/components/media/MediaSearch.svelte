<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    export let mediaType = 'movie';

    let searchQuery = '';
    let searchResults = [];
    let isLoading = false;
    let error = null;
    let selectedMedia = null;

    async function performSearch() {
        if (searchQuery.length < 2) {
            searchResults = [];
            return;
        }

        isLoading = true;
        error = null;

        try {
            const response = await fetch(`/api/v1/proxy/${mediaType}/search?query=${encodeURIComponent(searchQuery)}`);
            
            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data = await response.json();
            searchResults = data || [];
        } catch (e) {
            error = e.message;
            searchResults = [];
        } finally {
            isLoading = false;
        }
    }

    async function addMediaToLibrary(media) {
        try {
            isLoading = true;
            error = null;

            const endpoint = mediaType === 'movie' 
                ? '/api/v1/proxy/radarr/movies'
                : mediaType === 'tv'
                ? '/api/v1/proxy/sonarr/series'
                : '/api/v1/proxy/lidarr/artists';

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(media)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to add media');
            }

            const result = await response.json();
            selectedMedia = result;
            
            alert(`Successfully added ${media.title} to library`);
        } catch (e) {
            error = e.message || 'Failed to add media to library';
        } finally {
            isLoading = false;
        }
    }

    $: if (searchQuery) {
        performSearch();
    }
</script>

<div class="media-search-container">
    <div class="search-input-container">
        <input 
            type="text" 
            bind:value={searchQuery} 
            placeholder={`Search ${mediaType}s...`}
            class="search-input"
            disabled={isLoading}
        />
        {#if isLoading}
            <div class="loading-spinner">🔄</div>
        {/if}
    </div>

    {#if error}
        <div class="error-message">{error}</div>
    {/if}

    <div class="search-results">
        {#each searchResults as media (media.id)}
            <div class="media-result">
                <div class="media-details">
                    <h3>{media.title}</h3>
                    <button 
                        on:click={() => addMediaToLibrary(media)}
                        class="add-to-library-btn"
                        disabled={isLoading}
                    >
                        {isLoading ? 'Adding...' : 'Add to Library'}
                    </button>
                </div>
            </div>
        {/each}
    </div>
</div>

<style>
    .media-search-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 1rem;
    }

    .search-input-container {
        position: relative;
        margin-bottom: 1rem;
    }

    .search-input {
        width: 100%;
        padding: 0.75rem;
        font-size: 1rem;
        border: 1px solid #333;
        background-color: #222;
        color: white;
        border-radius: 4px;
    }

    .loading-spinner {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        animation: spin 1s linear infinite;
    }

    .search-results {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
    }

    .media-result {
        background-color: #1a1a1a;
        border-radius: 8px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s;
    }

    .add-to-library-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
        width: 100%;
    }

    .add-to-library-btn:disabled {
        background-color: #888;
        cursor: not-allowed;
    }

    .error-message {
        color: red;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background-color: rgba(255, 0, 0, 0.1);
        border-radius: 4px;
    }

    @keyframes spin {
        0% { transform: translateY(-50%) rotate(0deg); }
        100% { transform: translateY(-50%) rotate(360deg); }
    }
</style>