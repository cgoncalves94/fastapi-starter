.PHONY: help migrate-status migrate-upgrade migrate-rollback migrate-create migrate-history db-reset dev-server install test lint docker-build docker-up docker-down docker-logs docker-shell docker-db-shell

# Default target
help:
	@echo "FastAPI + SQLModel + PostgreSQL + Docker Project Commands"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  make docker-build      - Build Docker images"
	@echo "  make docker-up         - Start all services (PostgreSQL + FastAPI)"
	@echo "  make docker-down       - Stop all services"
	@echo "  make docker-logs       - View logs from all services"
	@echo "  make docker-shell      - Open shell in FastAPI container"
	@echo "  make docker-db-shell   - Open PostgreSQL shell"
	@echo "  make docker-pgadmin    - Start with PgAdmin (database UI)"
	@echo ""
	@echo "🗃️ Database Migrations:"
	@echo "  make migrate-status    - Show current migration status"
	@echo "  make migrate-upgrade   - Apply all pending migrations"
	@echo "  make migrate-rollback  - Rollback one migration"
	@echo "  make migrate-create MSG='message' - Create new migration"
	@echo "  make migrate-history   - Show migration history"
	@echo "  make db-reset         - Reset database (DANGER!)"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev-server       - Start development server (local)"
	@echo "  make install         - Install dependencies"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linting"

# ===================
# DOCKER COMMANDS
# ===================

docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build
	@echo "✅ Docker images built successfully!"

docker-up:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "✅ Services started! App: http://localhost:8000, Docs: http://localhost:8000/docs"

docker-down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ Services stopped!"

docker-logs:
	@echo "📋 Viewing logs..."
	docker-compose logs -f

docker-shell:
	@echo "🐚 Opening shell in FastAPI container..."
	docker-compose exec app /bin/bash

docker-db-shell:
	@echo "🗃️ Opening PostgreSQL shell..."
	docker-compose exec postgres psql -U postgres -d fastapi_starter

docker-pgadmin:
	@echo "🚀 Starting with PgAdmin..."
	docker-compose --profile tools up -d
	@echo "✅ PgAdmin UI: http://localhost:5050"

docker-restart:
	@echo "🔄 Restarting services..."
	docker-compose restart
	@echo "✅ Services restarted!"

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Docker cleanup completed!"

# ===================
# DATABASE MIGRATIONS
# ===================

migrate-status:
	@echo "📊 Current migration status:"
	python -m alembic current

migrate-upgrade:
	@echo "⬆️  Applying migrations..."
	python -m alembic upgrade head
	@echo "✅ Migrations applied successfully!"

migrate-rollback:
	@echo "⬇️  Rolling back last migration..."
	python -m alembic downgrade -1
	@echo "✅ Rollback completed!"

migrate-create:
ifndef MSG
	$(error MSG is required. Usage: make migrate-create MSG='Add user profile fields')
endif
	@echo "📝 Creating new migration: $(MSG)"
	python -m alembic revision --autogenerate -m "$(MSG)"
	@echo "✅ Migration created successfully!"

migrate-history:
	@echo "📚 Migration history:"
	python -m alembic history

db-reset:
	@echo "🚨 WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	python -m alembic upgrade head
	@echo "✅ Database reset completed!"

# Development Commands
dev-server:
	@echo "🚀 Starting development server..."
	fastapi dev src/app/main.py

install:
	@echo "📦 Installing dependencies..."
	uv sync
	@echo "✅ Dependencies installed!"

test:
	@echo "🧪 Running tests..."
	python -m pytest
	@echo "✅ Tests completed!"

lint:
	@echo "🔍 Running linters..."
	pre-commit run --all-files
	@echo "✅ Linting completed!"

# ===================
# DATABASE INSPECTION
# ===================

db-schema:
	@echo "📋 Database schema:"
	docker-compose exec postgres psql -U postgres -d fastapi_starter -c "\d"

db-tables:
	@echo "📊 Database tables:"
	docker-compose exec postgres psql -U postgres -d fastapi_starter -c "\dt"

db-info:
	@echo "ℹ️  Database info:"
	@echo "📍 PostgreSQL Database: fastapi_starter"
	@echo "📊 Tables:"
	@docker-compose exec postgres psql -U postgres -d fastapi_starter -c "\dt"
	@echo ""
	@echo "📈 Row counts:"
	@docker-compose exec postgres psql -U postgres -d fastapi_starter -c "SELECT 'users: ' || COUNT(*) FROM users UNION ALL SELECT 'workspaces: ' || COUNT(*) FROM workspaces UNION ALL SELECT 'workspace_members: ' || COUNT(*) FROM workspace_members;"

db-backup:
	@echo "💾 Creating database backup..."
	docker-compose exec postgres pg_dump -U postgres fastapi_starter > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created!"

db-restore:
ifndef BACKUP_FILE
	$(error BACKUP_FILE is required. Usage: make db-restore BACKUP_FILE=backup_20250101_120000.sql)
endif
	@echo "🔄 Restoring database from $(BACKUP_FILE)..."
	docker-compose exec -T postgres psql -U postgres -d fastapi_starter < $(BACKUP_FILE)
	@echo "✅ Database restored!"
