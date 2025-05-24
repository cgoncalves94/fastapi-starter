.PHONY: help migrate-status migrate-upgrade migrate-rollback migrate-create migrate-history db-reset dev-server install test lint

# Default target
help:
	@echo "FastAPI + SQLModel Project Commands"
	@echo ""
	@echo "Database Migrations:"
	@echo "  make migrate-status     - Show current migration status"
	@echo "  make migrate-upgrade    - Apply all pending migrations"
	@echo "  make migrate-rollback   - Rollback one migration"
	@echo "  make migrate-create MSG='message' - Create new migration"
	@echo "  make migrate-history    - Show migration history"
	@echo "  make db-reset          - Reset database (DANGER!)"
	@echo ""
	@echo "Development:"
	@echo "  make dev-server        - Start development server"
	@echo "  make install          - Install dependencies"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run linting"

# Database Migration Commands
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
	rm -f app.db
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

# Database inspection (bonus commands)
db-schema:
	@echo "📋 Database schema:"
	sqlite3 app.db ".schema"

db-tables:
	@echo "📊 Database tables:"
	sqlite3 app.db ".tables"

db-info:
	@echo "ℹ️  Database info:"
	@echo "📍 Location: app.db"
	@echo "📊 Tables:"
	@sqlite3 app.db ".tables"
	@echo ""
	@echo "📈 Row counts:"
	@sqlite3 app.db "SELECT 'users: ' || COUNT(*) FROM users; SELECT 'workspaces: ' || COUNT(*) FROM workspaces; SELECT 'workspace_members: ' || COUNT(*) FROM workspace_members;"
