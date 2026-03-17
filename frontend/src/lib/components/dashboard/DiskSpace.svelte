<script>
    import { onMount } from "svelte";
    import { getBackendUrl } from "$lib/stores";

    let services = [];
    let isLoading = true;
    let error = null;
    let totalServices = 0;
    let onlineServices = 0;

    async function fetchDiskSpace() {
        try {
            isLoading = true;
            error = null;
            const backendUrl = await getBackendUrl();
            const response = await fetch(
                `${backendUrl}/api/v1/system/disk-space`,
            );

            if (!response.ok) {
                throw new Error("Failed to fetch disk space");
            }

            const data = await response.json();
            services = data.services || [];
            totalServices = data.total_services || 0;
            onlineServices = data.online_services || 0;
        } catch (e) {
            error = e.message;
            services = [];
        } finally {
            isLoading = false;
        }
    }

    function getServiceIcon(name) {
        const icons = {
            radarr: "🎬",
            sonarr: "📺",
            lidarr: "🎵",
        };
        return icons[name.toLowerCase()] || "📦";
    }

    function getServiceColor(name) {
        const colors = {
            radarr: "#ff6b6b",
            sonarr: "#4ecdc4",
            lidarr: "#ffe66d",
        };
        return colors[name.toLowerCase()] || "#888";
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
    {:else if services.length === 0}
        <div class="empty">No services configured</div>
    {:else}
        <div class="services">
            {#each services as service}
                {#if service.disk_spaces.length > 0}
                    <div class="service-section">
                        <div class="service-header" style="border-left-color: {getServiceColor(service.name)}">
                            <span class="service-icon">{getServiceIcon(service.name)}</span>
                            <span class="service-name">{service.display_name}</span>
                            {#if service.status === 'offline'}
                                <span class="status-badge offline">Offline</span>
                            {:else if service.status === 'not_configured'}
                                <span class="status-badge not-configured">Not Configured</span>
                            {/if}
                        </div>
                        
                        {#if service.status === 'online'}
                            <div class="disk-spaces">
                                {#each service.disk_spaces as space}
                                    <div class="disk-space-item">
                                        <div class="path-info">
                                            <span class="path">{space.path}</span>
                                            {#if space.label && space.label !== space.path}
                                                <span class="label">({space.label})</span>
                                            {/if}
                                        </div>
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
                                                <span>{space.used_gb} GB / {space.total_gb} GB</span>
                                                <span>{space.free_gb} GB Free ({space.percent_used}%)</span>
                                            </div>
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        {:else if service.error}
                            <div class="service-error">{service.error}</div>
                        {/if}
                    </div>
                {/if}
            {/each}
        </div>
        
        <div class="summary">
            <span>{onlineServices}/{totalServices} services online</span>
        </div>
    {/if}
</div>

<style>
    .disk-space-container {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 1rem;
    }

    .loading,
    .error,
    .empty {
        color: #888;
        text-align: center;
        padding: 1rem;
    }

    .error {
        color: #f44336;
    }

    .services {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .service-section {
        background-color: #2a2a2a;
        border-radius: 8px;
        overflow: hidden;
    }

    .service-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        background-color: #333;
        border-left: 4px solid #888;
    }

    .service-icon {
        font-size: 1.25rem;
    }

    .service-name {
        font-weight: 600;
        color: #fff;
        flex: 1;
    }

    .status-badge {
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: 500;
    }

    .status-badge.offline {
        background-color: #f44336;
        color: #fff;
    }

    .status-badge.not-configured {
        background-color: #666;
        color: #ccc;
    }

    .disk-spaces {
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .disk-space-item {
        background-color: #1a1a1a;
        border-radius: 6px;
        padding: 0.75rem 1rem;
    }

    .path-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .path {
        font-weight: 600;
        color: #ddd;
        font-size: 0.9rem;
    }

    .label {
        color: #888;
        font-size: 0.85rem;
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
        background-color: #4caf50;
        transition: width 0.5s ease;
    }

    .progress.warning {
        background-color: #ffc107;
    }

    .progress.critical {
        background-color: #f44336;
    }

    .space-details {
        display: flex;
        justify-content: space-between;
        color: #888;
        font-size: 0.875rem;
    }

    .service-error {
        padding: 1rem;
        color: #f44336;
        font-size: 0.875rem;
        background-color: #1a1a1a;
        margin: 0 1rem 1rem 1rem;
        border-radius: 4px;
    }

    .summary {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #333;
        text-align: center;
        color: #888;
        font-size: 0.875rem;
    }
</style>
