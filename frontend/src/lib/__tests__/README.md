# Frontend Component Tests

Unit and integration tests for Svelte components and stores in the orchestratorr frontend.

## Test Files

### statusStore.test.js
Tests for the `statusStore.js` module.

**Coverage:**
- Store initialization with default values
- Service status initialization (all unknown)
- Version initialization (all null)
- refreshStatus() function
- isAnyServiceDown derived store logic
  - False when all services online
  - True when any service offline
  - True when backend error exists
- initializeStatusPolling() setup and cleanup
- Service timeout handling (AbortController)
- Degraded status detection (3+ second response time)
- Backend error handling and recovery
- Parallel request execution

**Test Count:** 16 tests

### StatusBadge.test.js
Tests for the `StatusBadge.svelte` component.

**Coverage:**
- Rendering with different status props (online/offline/degraded/unknown)
- Visual indicator colors
  - Green classes for online
  - Red classes for offline
  - Yellow classes for degraded
  - Gray classes for unknown
- Compact mode sizing
- Pulse animation for online status
- Default prop values (status='unknown', compact=false)
- Status text display
- CSS class application

**Test Count:** 13 tests

### StatusGrid.test.js
Tests for the `StatusGrid.svelte` component.

**Coverage:**
- Component mounting and rendering
- Header and refresh button display
- Service card rendering (4 services)
- Error banner display when backendError is set
- Error banner hidden when backendError is null
- Status summary text
  - "All Systems Operational" when all services online
  - "Service Degraded" when any service offline
  - "System Offline" when backend error exists
- Last-checked timestamp display
- "Never" display for uninitialized timestamps
- Service icons and labels (Radarr, Sonarr, Lidarr, Prowlarr)
- Version information display
- Auto-refresh message display (every 30 seconds)
- Responsive grid layout with CSS classes

**Test Count:** 18 tests

## Running Tests

### Install Dependencies

```bash
npm install
npm install -D vitest @sveltejs/vite-plugin-svelte jsdom
```

### Run All Tests

```bash
npm test
# or
npm run test:unit
```

### Run Specific Test File

```bash
npm test -- statusStore.test.js
npm test -- StatusBadge.test.js
npm test -- StatusGrid.test.js
```

### Watch Mode

```bash
npm test -- --watch
```

### Generate Coverage Report

```bash
npm test -- --coverage
```

## Test Configuration

- **Framework:** Vitest
- **DOM:** jsdom (simulates browser environment)
- **Coverage:** v8 provider with HTML/JSON/text reporters
- **Globals:** Enabled (describe, it, expect, beforeEach, etc.)

Configuration: `vitest.config.js`

## Expected Coverage

- statusStore.js: ~90%
- StatusBadge.svelte: ~85%
- StatusGrid.svelte: ~80% (lifecycle hooks and event handlers)

**Target Overall:** >85% code coverage

## Notes

- Tests use mocking for fetch/fetch calls to avoid network dependencies
- Component tests check rendered output and class names
- Store tests validate state changes and derived values
- All async operations are properly awaited or handled with Promises
- Error handling is tested for network failures and timeouts

## Future Improvements

1. Add visual regression tests using Percy or similar
2. Add E2E tests with Playwright for full user flows
3. Add performance benchmarks for polling efficiency
4. Add accessibility tests (a11y)
5. Expand error scenario coverage
