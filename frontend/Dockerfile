# Frontend Dockerfile for orchestratorr
# Multi-stage build: builder -> nginx
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
# Using npm install instead of npm ci because package-lock.json is excluded by .gitignore
RUN npm install

# Copy source code
COPY . .

# Debug: show current directory and svelte.config.js
RUN echo "=== Current directory structure ===" && ls -la && \
    echo "=== Current svelte.config.js ===" && cat svelte.config.js 2>/dev/null || echo "No svelte.config.js found"

# Build the application with environment variables
ARG VITE_API_BASE=http://localhost:8000
ENV VITE_API_BASE=${VITE_API_BASE}
ARG VITE_ADAPTER=static
ENV VITE_ADAPTER=${VITE_ADAPTER}
ARG VITE_RADARR_URL=http://localhost:7878
ENV VITE_RADARR_URL=${VITE_RADARR_URL}
ARG VITE_SONARR_URL=http://localhost:8989
ENV VITE_SONARR_URL=${VITE_SONARR_URL}
ARG VITE_LIDARR_URL=http://localhost:8686
ENV VITE_LIDARR_URL=${VITE_LIDARR_URL}
ARG VITE_PROWLARR_URL=http://localhost:9696
ENV VITE_PROWLARR_URL=${VITE_PROWLARR_URL}
# Debug: show environment variables
RUN echo "=== Build environment variables ===" && \
    echo "VITE_API_BASE=$VITE_API_BASE" && \
    echo "VITE_ADAPTER=$VITE_ADAPTER" && \
    echo "VITE_RADARR_URL=$VITE_RADARR_URL" && \
    echo "VITE_SONARR_URL=$VITE_SONARR_URL" && \
    echo "VITE_LIDARR_URL=$VITE_LIDARR_URL" && \
    echo "VITE_PROWLARR_URL=$VITE_PROWLARR_URL"

# Run build with more visibility
RUN echo "=== Starting build ===" && \
    npm run build 2>&1 | tee /tmp/build.log && \
    BUILD_EXIT=$? && \
    echo "=== Build exit code: $BUILD_EXIT ===" && \
    echo "=== Build log tail ===" && \
    tail -50 /tmp/build.log && \
    echo "=== Checking build output ===" && \
    if [ -d /app/build ]; then \
        echo "Build directory exists:" && \
        ls -la /app/build/ && \
        echo "=== Looking for index.html ===" && \
        find /app/build -name "*.html" -type f | head -10; \
    else \
        echo "ERROR: Build directory /app/build not found!" && \
        echo "=== Current directory contents ===" && \
        ls -la; \
    fi && \
    # Exit if build failed \
    if [ $BUILD_EXIT -ne 0 ]; then \
        echo "ERROR: Build failed with exit code $BUILD_EXIT"; \
        exit $BUILD_EXIT; \
    fi

# Production stage with nginx
FROM nginx:alpine

# Debug: show what's being copied (run in builder context)
COPY --from=builder /tmp/build.log /tmp/build.log

# Copy built static files
COPY --from=builder /app/build /usr/share/nginx/html

# Debug: verify copied files
RUN echo "=== Verifying nginx files ===" && \
    echo "NGINX root directory:" && \
    ls -la /usr/share/nginx/html/ 2>/dev/null || echo "No files in nginx root" && \
    echo "=== Looking for HTML files ===" && \
    find /usr/share/nginx/html -name "*.html" -type f 2>/dev/null | head -10 || echo "No HTML files found"

# Ensure nginx user can read the files
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

# Debug: show nginx config
RUN echo "=== Nginx configuration ===" && \
    cat /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]