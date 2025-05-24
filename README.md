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

## 🗄️ Database Models

### User
- Authentication and user management
- Profile information (email, username, full_name)
- Active/inactive status
- Superuser capabilities

### Workspace
- Team/organization containers
- Unique slugs for easy access
- Activation status
- Description and metadata

### WorkspaceMember
- Many-to-many relationship between users and workspaces
- Role-based permissions (Owner, Admin, Member, Viewer)
- Invitation tracking with timestamps

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
   uv venv --python 3.11 # Creates a .venv directory with python 3.11 (or your preferred Python version)
   source .venv/bin/activate # On Windows use .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   uv sync
   ```

5. Run the application using FastAPI CLI:
   ```bash
   uv run fastapi dev src/main.py
   ```

### Configuration

Edit the `.env` file to configure:
- Database URL (supports PostgreSQL and SQLite)
- JWT secret key and expiration
- CORS settings
- Debug mode

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user and get JWT token
- `GET /api/v1/auth/me` - Get current user information

### Users
- `GET /api/v1/users/` - List users with pagination (superuser only)
- `POST /api/v1/users/` - Create user (superuser only)
- `GET /api/v1/users/{user_id}` - Get user details
- `PATCH /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user (superuser only)
- `PATCH /api/v1/users/{user_id}/deactivate` - Deactivate user (superuser only)

### Workspaces
- `POST /api/v1/workspaces/` - Create workspace
- `GET /api/v1/workspaces/` - Get user's workspaces (paginated)
- `GET /api/v1/workspaces/all` - Get all workspaces (superuser only)
- `GET /api/v1/workspaces/{workspace_id}` - Get workspace details
- `GET /api/v1/workspaces/slug/{slug}` - Get workspace by slug
- `PATCH /api/v1/workspaces/{workspace_id}` - Update workspace
- `DELETE /api/v1/workspaces/{workspace_id}` - Delete workspace

### Workspace Members
- `GET /api/v1/workspaces/{workspace_id}/members` - Get workspace members
- `POST /api/v1/workspaces/{workspace_id}/members` - Add member to workspace
- `PATCH /api/v1/workspaces/{workspace_id}/members/{user_id}` - Update member role
- `DELETE /api/v1/workspaces/{workspace_id}/members/{user_id}` - Remove member
- `DELETE /api/v1/workspaces/{workspace_id}/leave` - Leave workspace

## 🔧 Development

### Code Style
- Modern Python syntax with type hints
- Async/await patterns throughout
- Dependency injection for clean testing
- Clean separation of concerns across layers
- Domain-driven exception handling

### Key Dependencies
- `fastapi` - Web framework
- `sqlmodel` - Database ORM
- `pydantic` - Data validation
- `passlib[bcrypt]` - Password hashing
- `pyjwt` - JWT tokens
- `uvicorn` - ASGI server

## 📖 Documentation

- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## 🧪 Usage Examples

### Register a new user
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123"
  }'
```

### Create a workspace
```bash
curl -X POST "http://localhost:8000/api/v1/workspaces/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "My Workspace",
    "slug": "my-workspace",
    "description": "A sample workspace"
  }'
```

## 📝 License

MIT License - see LICENSE file for details.
