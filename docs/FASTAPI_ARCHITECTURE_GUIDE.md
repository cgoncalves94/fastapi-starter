# FastAPI Clean Architecture Guide — (2025)

FastAPI + SQLModel + PostgreSQL clean‑architecture best‑practices guide. **Async‑first, Pydantic‑powered, production‑oriented** — use `async def` endpoints, `AsyncSession` with SQLModel, and enforce Pydantic validation at both the request and domain layers.

---

## 📋 Table of Contents

1. [Exception Handling Strategy](#exception-handling-strategy)
2. [Layer Responsibilities](#layer-responsibilities)
3. [Authentication vs Authorization](#authentication-vs-authorization)
4. [Dependency Injection](#dependency-injection)
5. [Transaction Management](#transaction-management)
6. [Database Integration](#database-integration)
7. [Best Practices & Gotchas](#best-practices--gotchas)
8. [Quick Reference](#quick-reference)

---

## 🏗️ Architecture Flow

```text
Request → Dependencies (HTTPException) → Router → Service (DomainException) → Repository (None) → Database
                     ↓
              Global Exception Handler (Domain → HTTP)
```

Each layer owns **exactly one** kind of exception.

---

## 🚨 Exception Handling Strategy

| Layer        | Behavior                     | Example                               |
| ------------ | ---------------------------- | ------------------------------------- |
| Dependencies | `fastapi.HTTPException`      | `HTTPException(401, "Invalid token")` |
| Services     | **Domain exceptions**        | `NotFoundError("User not found")`     |
| Repositories | *Return `None`* on not‑found | `return None`                         |

### Exception Architecture

* **Domain exceptions** inherit from a base `DomainException` class
* **Global exception handlers** convert domain exceptions to appropriate HTTP responses (registered in `main.py`)
* **SQLAlchemy errors** are caught and converted to clean user messages (no internal tracebacks exposed)
* **Unhandled exceptions** fall back to a generic "Internal server error" message

This ensures users never see internal tracebacks or sensitive system information.

---

## 🏛️ Layer Responsibilities

### Repository

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        # SQLModel .get returns instance | None
        return await self.session.get(User, user_id)
```

**Responsibilities**

* Execute CRUD and read‑only queries with SQLModel/SQLAlchemy.
* Receive an **`AsyncSession`** via DI; do **not** open/close connections itself.
* Return **either** an entity instance or `None` when not found.
* Use `flush()` instead of `commit()` to allow session dependency to manage transactions.

**Not responsible for**

* Business validation or cross‑entity rules.
* HTTP concerns.
* Managing transactions (session dependency handles commit/rollback).

### Service

```python
class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserResponse.model_validate(user)  # Pydantic v2
```

**Responsibilities**

* Enforce business rules and complex authorization logic.
* Coordinate multiple repositories within the same transaction.
* Transform and validate domain data (e.g., hash passwords).
* Raise domain exceptions (`NotFoundError`, `ConflictError`, etc.).
* Return Pydantic schemas (DTOs) rather than ORM models to decouple API responses from the database structure.

**Not responsible for**

* Managing database sessions or transactions.
* HTTP layer details (status codes, request/response objects).
* Authenticating users (handled by dependencies).

### Router

```python
@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: UUID, svc: UserService = Depends(get_user_service)):
    return await svc.get_user_by_id(user_id)
```

**Responsibilities**
* Handle HTTP-specific concerns: request parsing, response formatting
* Wire dependencies from version-specific dependency modules
* Located in `api/v{version}/routers/` for version isolation

**Not responsible for**
* Business logic (handled by services)
* Cross-version compatibility (each version has its own routers)

---

## 🔐 Authentication vs Authorization

* **Authentication** dependency (`get_current_user`) → validates JWT; raises `401`.
* **Authorization** dependency (`check_workspace_admin`) → coarse role / ownership check; raises `403`.
* Deeper, resource‑state‑dependent authorization belongs in **services** (domain exceptions).

---

## 🎯 Dependency Injection

### Session Dependency

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Session with automatic commit/rollback per request."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()  # Commit on success
        except Exception:
            await session.rollback()  # Rollback on any exception
            raise

SessionDep = Annotated[AsyncSession, Depends(get_session)]
```

### Factory Functions

```python
async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository=user_repository)

async def get_workspace_service(
    user_repository: UserRepository = Depends(get_user_repository),
    workspace_repository: WorkspaceRepository = Depends(get_workspace_repository),
) -> WorkspaceService:
    return WorkspaceService(
        user_repository=user_repository,
        workspace_repository=workspace_repository,
    )
```

---

## 🔄 Transaction Management

### How Multi-Repository Operations Work

This approach ensures atomicity for operations involving multiple repositories:

1. **Single Session Per Request**: All repositories share the same `AsyncSession`
2. **Repositories Use `flush()`**: Changes are staged but not committed individually
3. **Service Coordinates**: Business logic spans multiple repository calls
4. **Session Dependency Commits**: Final commit/rollback happens automatically

### Benefits

* ✅ **Automatic transaction boundaries** per request
* ✅ **Multi-repository atomicity** (e.g., `create_workspace` + `add_owner`)
* ✅ **Exception-safe rollbacks** for any domain errors
* ✅ **No manual UoW registration** needed for new repositories

---

## 🗃️ Database Integration

Uses **PostgreSQL** with **asyncpg** driver for optimal async performance:

```python
# src/app/core/database.py
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,  # Validates connections
    pool_recycle=300,    # Connection recycling
)
```

### Session Management

```python
# Async session factory
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Session dependency with automatic commit/rollback
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Key Benefits

* **Native UUID support** with `uuid-ossp` extension
* **Async connection pooling** for high concurrency
* **JSONB columns** for flexible data structures
* **Full-text search** capabilities built-in
* **Robust transaction management** with proper isolation

---

## 📋 Best Practices & Gotchas

1. Type‑hint repo returns (`-> Entity | None`) so static checkers force null handling.
2. Avoid service‑to‑service calls—share logic via helpers or coordinate via multiple repositories.
3. Keep the router thin; put all business rules in services.
4. One `DomainException` keeps the global handler tiny.
5. Repositories use `flush()` instead of `commit()` to work with session-level transactions.
6. **Always use async sessions** with PostgreSQL for optimal performance.
7. **Enable connection pooling** for production deployments.

---

## 🚀 Quick Reference

### Request Flow

```
HTTP Request → Router → Service → Repository → Database
```

### What Each Layer Does

| Layer          | Purpose         | Returns          | Raises            |
| -------------- | --------------- | ---------------- | ----------------- |
| **Router**     | HTTP handling   | Service response | Nothing           |
| **Service**    | Business logic  | Pydantic schemas | Domain exceptions |
| **Repo**       | Data access     | Models or `None` | Nothing           |
| **Dependency** | Auth/validation | Injected values  | `HTTPException`   |
