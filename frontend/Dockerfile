# Frontend Dockerfile for orchestratorr
# Multi-stage build: builder -> nginx
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
# Using npm install instead of npm ci because package-lock.json is excluded by .gitignore
RUN npm install

# Install static adapter for SvelteKit (required for nginx static hosting)
RUN npm install @sveltejs/adapter-static

# Copy source code
COPY . .

# Create production svelte.config.js for adapter-static
RUN rm -f svelte.config.js && cat > svelte.config.js << 'EOF'
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),
	kit: {
		adapter: adapter({
			pages: 'build',
			assets: 'build',
			fallback: '200.html',
			precompress: false,
			strict: true
		})
	}
};

export default config;
EOF

# Build the application with environment variables
ARG VITE_API_BASE=http://localhost:8000
ENV VITE_API_BASE=${VITE_API_BASE}
ARG VITE_RADARR_URL=http://localhost:7878
ENV VITE_RADARR_URL=${VITE_RADARR_URL}
ARG VITE_SONARR_URL=http://localhost:8989
ENV VITE_SONARR_URL=${VITE_SONARR_URL}
ARG VITE_LIDARR_URL=http://localhost:8686
ENV VITE_LIDARR_URL=${VITE_LIDARR_URL}
ARG VITE_PROWLARR_URL=http://localhost:9696
ENV VITE_PROWLARR_URL=${VITE_PROWLARR_URL}
RUN npm run build && \
    echo "Build completed successfully" && \
    ls -la /app/build/ 2>/dev/null || echo "Build directory not found"

# Production stage with nginx
FROM nginx:alpine

# Copy built static files
COPY --from=builder /app/build /usr/share/nginx/html

# Ensure nginx user can read the files
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
