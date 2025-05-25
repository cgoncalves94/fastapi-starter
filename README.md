# FastAPI Starter Project

A modern FastAPI starter project with SQLModel, Pydantic v2, and PostgreSQL/SQLite support. It features user authentication, workspace management with role-based access control, and a **Vertical (Feature-First) Architecture** for enhanced scalability and maintainability.

## 🚀 Features

- **Modern Python**: Uses Python 3.11+ with modern syntax
- **FastAPI**: Latest FastAPI with async/await support
- **SQLModel**: Type-safe database operations with SQLModel
- **Pydantic v2**: Data validation with Pydantic v2 and modern configuration
- **Authentication**: JWT-based authentication with password hashing
- **Role-based Access**: Workspace-based permissions with different roles
- **Clean Architecture**: **Vertical (Feature-First) Architecture**, Repository pattern, service layer, and dependency injection
- **Exception Handling**: Domain-driven exception handling with global handlers
- **Alembic Migrations**: Database schema management with Alembic
- **Modern Linting & Formatting**: Configured with Ruff, MyPy, Bandit, and Pytest for automated code quality.

## 🏗️ Architecture

```
src/app/
├── main.py                    # FastAPI app initialization
├── core/                      # Shared infrastructure (config, db, security, exceptions)
├── api/v1/                    # API layer (router aggregation, shared dependencies)
├── users/                     # Users Domain (models, schemas, repository, service, router)
├── workspaces/                # Workspaces Domain (models, schemas, repository, service, router)
└── auth/                      # Auth Domain (schemas, service, router)
```

For more details about the Vertical (Feature-First) Architecture implementation, see the [FastAPI Clean Architecture Guide](docs/FASTAPI_ARCHITECTURE_GUIDE.md).

##  Getting Started

### Prerequisites

- Python 3.11+
- uv (recommended) or pip

### Installation

1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

3. Create and activate a virtual environment using `uv`:
   ```bash
   uv venv --python 3.11
   source .venv/bin/activate
   ```

4. Use `make` to manage the project:

   See the "Usage" section below for available commands.

## 🚀 Usage

Use `make` to simplify common development tasks:

* `make install` - Install dependencies
* `make dev-server` - Run the development server
* `make lint` - Run linters
* `make test` - Run tests
* `make migrate-create MSG="Your migration message"` - Create a new migration
* `make migrate-upgrade` - Apply all pending migrations
* `make migrate-rollback` - Rollback one migration
* `make migrate-status` - Show current migration status
* `make migrate-history` - Show migration history

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

* **Swagger UI**: Visit `/docs` for interactive API exploration and testing
* **ReDoc**: Visit `/redoc` for alternative documentation format
* **OpenAPI JSON**: Available at `/openapi.json` for API specification

When running locally (`make dev-server`), access the documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

### Configuration

Edit the `.env` file to configure:
- Database URL (supports PostgreSQL and SQLite)
- JWT secret key and expiration
- CORS settings
- Debug mode

For detailed instructions on database schema management and migrations, see the [Alembic Migrations Guide](docs/ALEMBIC_MIGRATIONS_GUIDE.md).

## 📝 License

MIT License - see LICENSE file for details.
