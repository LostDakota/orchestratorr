<script>
    import { onMount } from 'svelte';

    export let paths = ['/movies', '/tv', '/music'];
    
    let diskSpaces = [];
    let isLoading = true;
    let error = null;

    async function fetchDiskSpace() {
        try {
            isLoading = true;
            const response = await fetch(`/api/v1/system/disk-space?${paths.map(p => `paths=${encodeURIComponent(p)}`).join('&')}`);
            
            if (!response.ok) {
                throw new Error('Failed to fetch disk space');
            }

            diskSpaces = await response.json();
        } catch (e) {
            error = e.message;
            diskSpaces = [];
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        fetchDiskSpace();
        
        // Refresh every 5 minutes
        const intervalId = setInterval(fetchDiskSpace, 5 * 60 * 1000);
        
        return () => clearInterval(intervalId);
    });
</script>

<div class="disk-space-container">
    <h2 class="text-2xl font-bold text-white mb-4">Disk Space</h2>
    
    {#if isLoading}
        <div class="loading">Loading disk space...</div>
    {:else if error}
        <div class="error">{error}</div>
    {:else}
        <div class="disk-spaces">
            {#each diskSpaces as space}
                <div class="disk-space-item">
                    <div class="path">{space.path}</div>
                    <div class="space-info">
                        <div class="progress-bar">
                            <div 
                                class="progress" 
                                style="width: {space.percent_used}%"
                                class:warning={space.percent_used > 80}
                                class:critical={space.percent_used > 90}
                            ></div>
                        </div>
                        <div class="space-details">
                            <span>{space.used.toFixed(1)} GB / {space.total.toFixed(1)} GB</span>
                            <span>{space.free.toFixed(1)} GB Free</span>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .disk-space-container {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 1rem;
    }

    .loading, .error {
        color: #888;
        text-align: center;
        padding: 1rem;
    }

    .disk-spaces {
        display: grid;
        gap: 1rem;
    }

    .disk-space-item {
        background-color: #2a2a2a;
        border-radius: 4px;
        padding: 1rem;
    }

    .path {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #ddd;
    }

    .progress-bar {
        height: 20px;
        background-color: #333;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }

    .progress {
        height: 100%;
        background-color: #4CAF50;
        transition: width 0.5s ease;
    }

    .progress.warning {
        background-color: #FFC107;
    }

    .progress.critical {
        background-color: #F44336;
    }

    .space-details {
        display: flex;
        justify-content: space-between;
        color: #888;
        font-size: 0.875rem;
    }
</style>