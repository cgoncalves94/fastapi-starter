# FastAPI Starter Project

A modern FastAPI starter project with SQLModel, Pydantic v2, PostgreSQL, and Docker support. It features user authentication, workspace management with role-based access control, and a **Vertical (Feature-First) Architecture** for enhanced scalability and maintainability.

## 🚀 Features

- **Modern Python**: Uses Python 3.13+ with modern syntax
- **FastAPI**: Latest FastAPI with async/await support
- **SQLModel**: Type-safe database operations with SQLModel
- **Pydantic v2**: Data validation with Pydantic v2 and modern configuration
- **PostgreSQL**: Production-ready PostgreSQL database with async support
- **Docker Support**: Containerized development and deployment with Docker Compose
- **Authentication**: JWT-based authentication with secure password hashing and email verification
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
│   └── routers/               # Version-specific HTTP routing layer
├── users/                     # Users Domain (models, schemas, repository, service)
├── workspaces/                # Workspaces Domain (models, schemas, repository, service)
└── auth/                      # Auth Domain (schemas, service)
```

For more details about the Vertical (Feature-First) Architecture implementation, see the [FastAPI Clean Architecture Guide](docs/FASTAPI_ARCHITECTURE_GUIDE.md).

## Getting Started

### Prerequisites

**Option 1: Docker (Recommended)**
- Docker and Docker Compose
- Git

**Option 2: Local Development**
- Python 3.13+
- PostgreSQL 17.5+
- uv (recommended) or pip

### 🐳 Quick Start with Docker

To get the project up and running for the first time with Docker:

1.  **Clone the repository:**
    ```bash
    git clone cgoncalves94/fastapi-starter
    cd fastapi-starter
    ```
2.  **Copy environment variables:**
    ```bash
    cp .env.example .env
    ```
3.  **Start the application services:**
    ```bash
    make docker-up
    ```
    This command will automatically build Docker images, start all services, and run database migrations.

4.  **Access the application:**
    -   **API**: http://localhost:8000
    -   **API Docs**: http://localhost:8000/docs
    -   **PgAdmin** (optional): `make docker-pgadmin` then visit http://localhost:5050

**Important Notes for Docker Usage:**

*   **`make docker-up` handles everything**: Database migrations are automatically applied during container startup via the Docker entrypoint script.
*   **For subsequent starts**: Just run `make docker-up` again - it will start containers without rebuilding unless needed.


### 🖥️ Local Development Setup

1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

3. Create and activate a virtual environment using `uv`:
   ```bash
   uv venv --python 3.13
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   make install
   ```

5. Run database migrations:
   ```bash
   make migrate-upgrade
   ```

6. Start the development server:
   ```bash
   make dev-server
   ```

## 🚀 Usage

### 🐳 Docker Commands

For containerized development:

* `make docker-build` - Build Docker images
* `make docker-up` - Start all services (PostgreSQL + FastAPI)
* `make docker-down` - Stop all services
* `make docker-logs` - View logs from all services
* `make docker-shell` - Open shell in FastAPI container
* `make docker-db-shell` - Open PostgreSQL shell
* `make docker-pgadmin` - Start with PgAdmin UI (http://localhost:5050)

### 🗃️ Database Commands

* `make migrate-create MSG="Your migration message"` - Create a new migration
* `make migrate-upgrade` - Apply all pending migrations
* `make migrate-rollback` - Rollback one migration
* `make migrate-status` - Show current migration status
* `make migrate-history` - Show migration history
* `make db-info` - Show database information
* `make db-backup` - Create database backup
* `make db-restore BACKUP_FILE="filename.sql"` - Restore from backup

### 🚀 Development Commands

* `make install` - Install dependencies
* `make dev-server` - Run the development server (local)
* `make lint` - Run linters
* `make test` - Run tests

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

* **Swagger UI**: Visit `/docs` for interactive API exploration and testing
* **ReDoc**: Visit `/redoc` for alternative documentation format
* **OpenAPI JSON**: Available at `/openapi.json` for API specification

When running locally (`make dev-server`), access the documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## ⚙️ Configuration

Edit the `.env` file to configure PostgreSQL connection and other settings:
- PostgreSQL host, port, user, password, and database name
- JWT secret key and expiration
- CORS settings
- Debug mode

For detailed instructions on database schema management and migrations, see the [Alembic Migrations Guide](docs/ALEMBIC_MIGRATIONS_GUIDE.md).

## 📝 License

MIT License - see LICENSE file for details.
