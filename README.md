# FastAPI Starter Project

A modern FastAPI starter project with SQLModel, Pydantic v2, and PostgreSQL/SQLite support. Features user authentication and workspace management with role-based access control.

## 🚀 Features

- **Modern Python**: Uses Python 3.11+ with modern syntax
- **FastAPI**: Latest FastAPI with async/await support
- **SQLModel**: Type-safe database operations with SQLModel
- **Pydantic v2**: Data validation with Pydantic v2 and modern configuration
- **Authentication**: JWT-based authentication with password hashing
- **Role-based Access**: Workspace-based permissions with different roles
- **Clean Architecture**: Repository pattern, service layer, and dependency injection
- **Exception Handling**: Domain-driven exception handling with global handlers
- **Alembic Migrations**: Database schema management with Alembic

## 🏗️ Architecture

```
src/
├── api/v1/
│   ├── dependencies/     # FastAPI dependencies (auth, authorization, database)
│   ├── models/          # SQLModel database models
│   ├── repositories/    # Data access layer
│   ├── routers/         # API endpoints (auth, users, workspaces)
│   ├── schemas/         # Pydantic schemas for request/response
│   └── services/        # Business logic layer
├── core/                # Core application logic
│   ├── config.py        # Settings and configuration
│   ├── database.py      # Database connection and session management
│   ├── security.py      # Auth utilities (JWT, password hashing)
│   ├── exceptions.py    # Custom domain exceptions
│   └── exception_handlers.py # Global exception handlers
└── main.py             # FastAPI app initialization
```

## 🔐 Authentication & Authorization

- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Multi-layer authorization:
  - Authentication dependencies (validate JWT tokens)
  - Authorization dependencies (role-based access checks)
  - Service-level business rule enforcement
- Protected endpoints with dependency injection

## 🚦 Getting Started

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

### Configuration

Edit the `.env` file to configure:
- Database URL (supports PostgreSQL and SQLite)
- JWT secret key and expiration
- CORS settings
- Debug mode

## 📝 License

MIT License - see LICENSE file for details.
