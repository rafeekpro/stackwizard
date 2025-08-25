.PHONY: help start stop restart status logs shell db-reset db-backup db-restore test clean build urls

# Default target
help:
	@echo "StackWizard Development Environment"
	@echo ""
	@echo "Available commands:"
	@echo "  make start        - Start all services"
	@echo "  make stop         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo "  make status       - Show service status"
	@echo "  make logs         - Show logs (all services)"
	@echo "  make logs-backend - Show backend logs"
	@echo "  make logs-frontend- Show frontend logs"
	@echo "  make shell        - Open backend shell"
	@echo "  make shell-db     - Open PostgreSQL shell"
	@echo "  make db-reset     - Reset database to initial state"
	@echo "  make db-backup    - Create database backup"
	@echo "  make db-restore   - Restore latest database backup"
	@echo "  make test         - Run all tests"
	@echo "  make clean        - Remove all containers and volumes"
	@echo "  make build        - Rebuild all containers"
	@echo "  make urls         - Show all service URLs"

# Service management
start:
	@./scripts/dev.sh start

stop:
	@./scripts/dev.sh stop

restart:
	@./scripts/dev.sh restart

status:
	@./scripts/dev.sh status

# Logging
logs:
	@./scripts/dev.sh logs

logs-backend:
	@./scripts/dev.sh logs backend

logs-frontend:
	@./scripts/dev.sh logs frontend

logs-db:
	@./scripts/dev.sh logs postgres

# Shell access
shell:
	@./scripts/dev.sh shell backend

shell-frontend:
	@./scripts/dev.sh shell frontend

shell-db:
	@./scripts/dev.sh shell db

shell-redis:
	@./scripts/dev.sh shell redis

# Database management
db-reset:
	@./scripts/dev.sh db:reset

db-backup:
	@./scripts/dev.sh db:backup

db-restore:
	@./scripts/dev.sh db:restore

db-migrate:
	@./scripts/dev.sh db:migrate

db-seed:
	@./scripts/dev.sh db:seed

# Testing
test:
	@./scripts/dev.sh test

test-backend:
	@docker-compose exec backend pytest tests/ -v

test-frontend:
	@docker-compose exec frontend npm test -- --watchAll=false

test-e2e:
	@docker-compose exec frontend npm run test:e2e

# Development utilities
format:
	@docker-compose exec backend black .
	@docker-compose exec frontend npm run format

lint:
	@docker-compose exec backend flake8 .
	@docker-compose exec frontend npm run lint

type-check:
	@docker-compose exec backend mypy .
	@docker-compose exec frontend npm run type-check

# Container management
clean:
	@./scripts/dev.sh clean

build:
	@./scripts/dev.sh build

rebuild: clean build start

# Information
urls:
	@./scripts/dev.sh urls

ps:
	@docker-compose ps

# Quick development commands
dev: start logs

fresh: clean build start

# Backend specific
backend-shell:
	@docker-compose exec backend python

backend-migrations:
	@docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

backend-migrate:
	@docker-compose exec backend alembic upgrade head

# Frontend specific
frontend-install:
	@docker-compose exec frontend npm install

frontend-build:
	@docker-compose exec frontend npm run build