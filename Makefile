.PHONY: help build up down logs test clean dev prod shell-backend shell-frontend onboard

# Default target
help:
	@echo "Orchestratorr Docker Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make init           - Initial setup (copy .env.example to .env)"
	@echo "  make onboard        - Interactive onboarding wizard (recommended)"
	@echo "  make build          - Build Docker images"
	@echo ""
	@echo "Running:"
	@echo "  make up             - Start services (production)"
	@echo "  make dev            - Start services with hot reload (development)"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make ps             - Show running services"
	@echo ""
	@echo "Logs:"
	@echo "  make logs           - Follow all logs"
	@echo "  make logs-backend   - Follow backend logs"
	@echo "  make logs-frontend  - Follow frontend logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-backend   - Run backend tests"
	@echo "  make test-frontend  - Run frontend tests"
	@echo ""
	@echo "Shell Access:"
	@echo "  make shell-backend  - Access backend shell"
	@echo "  make shell-frontend - Access frontend shell"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Stop and remove containers, keep images"
	@echo "  make clean-all      - Stop, remove containers, images, and volumes"
	@echo "  make prune          - Remove all unused Docker resources"
	@echo ""
	@echo "Advanced:"
	@echo "  make build-no-cache - Rebuild without using cache"
	@echo "  make config         - Show Docker Compose config"
	@echo "  make validate       - Validate Docker Compose file"

# Setup
init:
	@if [ -f .env ]; then \
		echo ".env already exists"; \
	else \
		cp .env.example .env; \
		echo "Created .env from .env.example - edit with your values"; \
	fi

onboard:
	@echo "Starting Orchestratorr Onboarding Wizard..."
	@cd backend && python onboard.py

# Build
build:
	docker-compose build

build-no-cache:
	docker-compose build --no-cache

# Running Services
up:
	docker-compose up -d
	@echo "Services started! Access at:"
	@echo "  Frontend: http://localhost"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "Development services started with hot reload!"
	@echo "  Frontend: http://localhost:5173"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart
	@echo "Services restarted"

ps:
	docker-compose ps

# Logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# Testing
test: test-backend test-frontend
	@echo "All tests completed"

test-backend:
	@echo "Running backend tests..."
	docker-compose exec -T backend python -m pytest

test-frontend:
	@echo "Running frontend tests..."
	docker-compose exec -T frontend npm test

# Shell Access
shell-backend:
	docker-compose exec backend sh

shell-frontend:
	docker-compose exec frontend sh

# Cleanup
clean:
	docker-compose down
	@echo "Containers stopped and removed (images preserved)"

clean-all:
	docker-compose down -v --rmi all
	@echo "All containers, volumes, and images removed"

prune:
	docker system prune -a
	@echo "Unused Docker resources removed"

# Configuration
config:
	docker-compose config

validate:
	docker-compose config --quiet && echo "Docker Compose file is valid"

# Utility targets
.PHONY: check-env
check-env:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found"; \
		echo "Run 'make init' to create it"; \
		exit 1; \
	fi

# Health check
health:
	@echo "Checking service health..."
	@echo ""
	@echo "Backend health:"
	@curl -s http://localhost:8000/health && echo "" || echo "FAILED"
	@echo ""
	@echo "Frontend health:"
	@curl -s -I http://localhost | head -1 || echo "FAILED"
	@echo ""
	@docker-compose ps

# Development convenience
rebuild-backend:
	docker-compose build backend && docker-compose restart backend

rebuild-frontend:
	docker-compose build frontend && docker-compose restart frontend

# Show logs from last N minutes
logs-recent:
	docker-compose logs --since 10m -f

# Execute commands in containers
exec-backend:
	@read -p "Enter command: " cmd; \
	docker-compose exec backend $$cmd

exec-frontend:
	@read -p "Enter command: " cmd; \
	docker-compose exec frontend $$cmd

# Full reset (WARNING: removes everything)
reset: clean-all init build up
	@echo "Full reset complete!"

# Show Docker Compose project info
info:
	@echo "Docker Compose Project: orchestratorr"
	@echo ""
	@echo "Services:"
	@docker-compose config --services
	@echo ""
	@echo "Networks:"
	@docker network ls | grep orchestr
	@echo ""
	@echo "Volumes:"
	@docker volume ls | grep orchestr
	@echo ""
	@echo "Images:"
	@docker image ls | grep orchestr

# One command to start everything fresh
fresh: clean-all init build up logs
	@echo "Fresh start complete! All systems running."
