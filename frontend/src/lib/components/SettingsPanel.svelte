<!--
Settings Panel Component

Allows users to configure application settings with localStorage persistence.
Settings include backend URL, theme, refresh interval, and advanced options.
-->

<script>
	import { configStore, resetConfig, setBackendUrl } from '../stores/appStore';
	import { get } from 'svelte/store';
	import { onMount, onDestroy } from 'svelte';

	let isOpen = false;
	let tempConfig = { ...configStore };
	let hasChanges = false;

	// Control body overflow when modal is open
	$: if (typeof document !== 'undefined') {
		if (isOpen) {
			document.body.classList.add('modal-open');
		} else {
			document.body.classList.remove('modal-open');
		}
	}

	onDestroy(() => {
		document.body.classList.remove('modal-open');
	});

	/**
	 * Load current config on mount
	 */
	const unsubscribe = configStore.subscribe((config) => {
		tempConfig = { ...config };
	});

	/**
	 * Handle setting change
	 */
	function handleConfigChange(key, value) {
		tempConfig[key] = value;
		hasChanges = true;
	}

	/**
	 * Save settings to store (auto-persists to localStorage)
	 */
	function saveSettings() {
		configStore.set(tempConfig);
		hasChanges = false;
		// Optional: show success notification
		console.log('Settings saved');
	}

	/**
	 * Reset to defaults
	 */
	function resetToDefaults() {
		if (window.confirm('Reset all settings to defaults?')) {
			resetConfig();
			hasChanges = false;
		}
	}

	/**
	 * Cancel changes
	 */
	function cancelChanges() {
		// Revert to current store value
		tempConfig = { ...get(configStore) };
		hasChanges = false;
	}

	onMount(() => {
		return unsubscribe;
	});
</script>

<div class="settings-panel">
	<!-- Toggle Button -->
	<button
		class="settings-button"
		on:click={() => (isOpen = !isOpen)}
		title="Open settings"
	>
		⚙️ Settings
	</button>

	<!-- Settings Modal -->
	{#if isOpen}
		<div class="modal-overlay" on:click={() => (isOpen = false)}>
			<div class="modal" on:click={(e) => e.stopPropagation()}>
				<!-- Header -->
				<div class="modal-header">
					<h2>Application Settings</h2>
					<button
						class="close-button"
						on:click={() => (isOpen = false)}
					>
						✕
					</button>
				</div>

				<!-- Content -->
				<div class="modal-content">
					<!-- Backend URL -->
					<div class="setting-group">
						<label for="backendUrl">Backend URL</label>
						<input
							id="backendUrl"
							type="text"
							value={tempConfig.backendUrl}
							on:change={(e) =>
								handleConfigChange('backendUrl', e.target.value)}
							placeholder="http://localhost:8000"
						/>
						<p class="hint">
							The URL of your orchestratorr FastAPI backend server
						</p>
					</div>

					<!-- Theme -->
					<div class="setting-group">
						<label for="theme">Theme</label>
						<select
							id="theme"
							value={tempConfig.theme}
							on:change={(e) =>
								handleConfigChange('theme', e.target.value)}
						>
							<option value="dark">Dark</option>
							<option value="light">Light</option>
						</select>
					</div>

					<!-- Refresh Interval -->
					<div class="setting-group">
						<label for="refreshInterval">Refresh Interval (seconds)</label>
						<input
							id="refreshInterval"
							type="number"
							min="5"
							max="300"
							value={tempConfig.refreshInterval}
							on:change={(e) =>
								handleConfigChange('refreshInterval', parseInt(e.target.value))}
						/>
						<p class="hint">
							How often to refresh service status (5-300 seconds)
						</p>
					</div>

					<!-- Advanced Options -->
					<div class="setting-group">
						<label for="showAdvanced">
							<input
								id="showAdvanced"
								type="checkbox"
								checked={tempConfig.showAdvanced}
								on:change={(e) =>
									handleConfigChange('showAdvanced', e.target.checked)}
							/>
							Show Advanced Options
						</label>
					</div>

					<!-- Info Box -->
					<div class="info-box">
						<p>
							<strong>Note:</strong> Settings are automatically saved to your browser's local
							storage and persist across sessions.
						</p>
					</div>
				</div>

				<!-- Footer -->
				<div class="modal-footer">
					<button class="btn-secondary" on:click={cancelChanges}>
						Cancel
					</button>
					<button class="btn-danger" on:click={resetToDefaults}>
						Reset Defaults
					</button>
					<button
						class="btn-primary"
						on:click={saveSettings}
						disabled={!hasChanges}
					>
						Save Settings
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.settings-panel {
		position: relative;
	}

	.settings-button {
		padding: 8px 16px;
		background-color: #4b5563;
		color: #fff;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		transition: background-color 0.2s;
	}

	.settings-button:hover {
		background-color: #5a6578;
	}

	.modal-overlay {
		position: fixed;
		inset: 0;
		width: 100vw;
		height: 100vh;
		background-color: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		overflow: auto;
		transform: translateZ(0);
	}

	.modal {
		background-color: #1f2937;
		border: 1px solid #374151;
		border-radius: 12px;
		width: 90%;
		max-width: 500px;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 24px;
		border-bottom: 1px solid #374151;
	}

	.modal-header h2 {
		margin: 0;
		font-size: 20px;
		color: #fff;
	}

	.close-button {
		background: none;
		border: none;
		color: #9ca3af;
		cursor: pointer;
		font-size: 24px;
		padding: 0;
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 4px;
		transition: background-color 0.2s;
	}

	.close-button:hover {
		background-color: #374151;
		color: #fff;
	}

	.modal-content {
		padding: 24px;
	}

	.setting-group {
		margin-bottom: 24px;
	}

	.setting-group label {
		display: block;
		margin-bottom: 8px;
		color: #e5e7eb;
		font-weight: 500;
		font-size: 14px;
	}

	.setting-group input[type='text'],
	.setting-group input[type='number'],
	.setting-group select {
		width: 100%;
		padding: 10px 12px;
		border: 1px solid #4b5563;
		border-radius: 6px;
		background-color: #111827;
		color: #e5e7eb;
		font-size: 14px;
	}

	.setting-group input[type='text']:focus,
	.setting-group input[type='number']:focus,
	.setting-group select:focus {
		outline: none;
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}

	.setting-group input[type='checkbox'] {
		margin-right: 8px;
	}

	.hint {
		margin-top: 6px;
		font-size: 12px;
		color: #9ca3af;
	}

	.info-box {
		background-color: #0f172a;
		border-left: 4px solid #3b82f6;
		padding: 12px;
		border-radius: 6px;
		font-size: 13px;
		color: #cbd5e1;
	}

	.info-box p {
		margin: 0;
	}

	.modal-footer {
		display: flex;
		gap: 12px;
		padding: 24px;
		border-top: 1px solid #374151;
		justify-content: flex-end;
	}

	.btn-primary,
	.btn-secondary,
	.btn-danger {
		padding: 10px 16px;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		transition: all 0.2s;
	}

	.btn-primary {
		background-color: #3b82f6;
		color: #fff;
	}

	.btn-primary:hover:not(:disabled) {
		background-color: #2563eb;
	}

	.btn-primary:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-secondary {
		background-color: #4b5563;
		color: #fff;
	}

	.btn-secondary:hover {
		background-color: #5a6578;
	}

	.btn-danger {
		background-color: #ef4444;
		color: #fff;
	}

	.btn-danger:hover {
		background-color: #dc2626;
	}
:global(body.modal-open) {
		overflow: hidden;
	}
</style>
