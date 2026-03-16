<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { debounce } from '$lib/utils/debounce';

    export let mediaType = 'movie';

    let searchQuery = '';
    let searchResults = [];
    let isLoading = false;
    let error = null;
    let selectedMedia = null;

    const performSearch = debounce(async () => {
        if (searchQuery.length < 2) {
            searchResults = [];
            return;
        }

        isLoading = true;
        error = null;

        try {
            const response = await fetch(`/api/v1/media/search?query=${encodeURIComponent(searchQuery)}&media_type=${mediaType}`);
            
            if (!response.ok) {
                throw new Error('Search failed');
            }

            const data = await response.json();
            searchResults = data.results || [];
        } catch (e) {
            error = e.message;
            searchResults = [];
        } finally {
            isLoading = false;
        }
    }, 300);

    async function addMediaToLibrary(media) {
        try {
            const response = await fetch('/api/v1/media/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    media_type: mediaType,
                    external_id: media.id,
                    title: media.title
                })
            });

            if (!response.ok) {
                throw new Error('Failed to add media');
            }

            const result = await response.json();
            selectedMedia = result;
            
            // Optional: Show success notification
            alert(`Added ${media.title} to library`);
        } catch (e) {
            error = e.message;
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
            placeholder="Search {mediaType}s..."
            class="search-input"
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
                {#if media.poster_path}
                    <img 
                        src={media.poster_path} 
                        alt={media.title} 
                        class="media-poster"
                    />
                {/if}
                <div class="media-details">
                    <h3>{media.title}</h3>
                    <p>{media.overview || 'No description available'}</p>
                    <div class="media-metadata">
                        {#if media.release_date}
                            <span>Release: {media.release_date}</span>
                        {/if}
                        {#if media.vote_average}
                            <span>Rating: {media.vote_average.toFixed(1)}</span>
                        {/if}
                    </div>
                    <button 
                        on:click={() => addMediaToLibrary(media)}
                        class="add-to-library-btn"
                    >
                        Add to Library
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

    .media-result:hover {
        transform: scale(1.05);
    }

    .media-poster {
        width: 100%;
        height: 375px;
        object-fit: cover;
    }

    .media-details {
        padding: 1rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex-grow: 1;
    }

    .media-metadata {
        display: flex;
        justify-content: space-between;
        margin: 0.5rem 0;
        color: #888;
    }

    .add-to-library-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.2s;
    }

    .add-to-library-btn:hover {
        background-color: #45a049;
    }

    .error-message {
        color: red;
        margin-bottom: 1rem;
    }

    @keyframes spin {
        0% { transform: translateY(-50%) rotate(0deg); }
        100% { transform: translateY(-50%) rotate(360deg); }
    }
</style>