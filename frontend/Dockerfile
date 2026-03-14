# Frontend Dockerfile for orchestratorr
# Multi-stage build: builder -> nginx
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm install

# Install static adapter for SvelteKit (required for nginx static hosting)
RUN npm install @sveltejs/adapter-static

# Copy source code
COPY . .

# Update svelte.config.js to use adapter-static instead of adapter-auto
RUN sed -i "s/adapter from '@sveltejs\/adapter-auto'/adapter from '@sveltejs\/adapter-static'/" svelte.config.js

# Build the application with environment variable
ARG VITE_API_BASE=http://localhost:8000
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built static files
COPY --from=builder /app/build /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
