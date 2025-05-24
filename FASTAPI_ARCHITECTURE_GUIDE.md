# FastAPI Clean Architecture Guide — (2025)

FastAPI + SQLModel clean‑architecture best‑practices guide. **Async‑first, Pydantic‑powered, production‑oriented** — use `async def` endpoints, `AsyncSession` with SQLModel, and enforce Pydantic validation at both the request and domain layers.

---

## 📋 Table of Contents

1. [Exception Handling Strategy](#exception-handling-strategy)
2. [Layer Responsibilities](#layer-responsibilities)
3. [Authentication vs Authorization](#authentication-vs-authorization)
4. [Async Essentials](#async-essentials)
5. [Dependency Injection & Factories](#dependency-injection--factories)
6. [Best Practices & Gotchas](#best-practices--gotchas)
7. [Final Flow & Cheat‑sheet](#final-flow--cheat-sheet)

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

| Layer        | Raises                       | Example                               |
| ------------ | ---------------------------- | ------------------------------------- |
| Dependencies | `fastapi.HTTPException`      | `HTTPException(401, "Invalid token")` |
| Services     | **Domain exceptions**        | `NotFoundError("User not found")`     |
| Repositories | *Return `None`* on not‑found | `return None`                         |

### Domain exception skeleton

```python
class BaseDomainError(Exception): ...
class NotFoundError(BaseDomainError): ...
class ConflictError(BaseDomainError): ...
class PermissionDeniedError(BaseDomainError): ...
class ValidationError(BaseDomainError): ...
```

### Global handler example

```python
@app.exception_handler(BaseDomainError)
async def domain_handler(_, exc: BaseDomainError):
    status_code = {
        NotFoundError: 404,
        ConflictError: 409,
        PermissionDeniedError: 403,
        ValidationError: 422,
    }.get(type(exc), 400)
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})

@app.exception_handler(Exception)  # safety net
async def unhandled(_, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
```

---

## 🏛️ Layer Responsibilities

### Repository

```python
class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)
```

**Responsibilities**

* Execute CRUD and read‑only queries with SQLModel/SQLAlchemy.
* Receive an **`AsyncSession`** via DI; do **not** open/close connections itself.
* Return an entity instance **or** `None` when not found.
* *Optionally* translate low‑level DB errors (e.g., `IntegrityError`) to **data‑centric** domain exceptions such as `ConflictError` – useful for keeping technical failures out of the service layer.

**Not responsible for**

* Business validation or cross‑entity rules.
* HTTP concerns.
* Managing transactions (session provider or Unit‑of‑Work handles commit/rollback).

### Service

```python
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user(self, user_id: int) -> UserRead:
        if (user := await self.repo.get(user_id)) is None:
            raise NotFoundError(user_id)
        return UserRead.model_validate(user)
```

**Responsibilities**

* Enforce business rules and complex authorization logic.
* Coordinate multiple repositories (or a Unit‑of‑Work).
* Transform and validate domain data (e.g., hash passwords).
* Raise domain exceptions (`NotFoundError`, `ConflictError`, etc.).

**Not responsible for**

* Managing database sessions or transactions.
* HTTP layer details (status codes, request/response objects).
* Authenticating users (handled by dependencies).

### Router

```python
@router.get("/users/{user_id}", response_model=UserRead)
async def read_user(user_id: int, svc: UserService = Depends(get_user_service)):
    return await svc.get_user(user_id)
```

Handles HTTP only—params, responses, DI wiring.

---

## 🔐 Authentication vs Authorization

* **Authentication** dependency (`get_current_user`) → validates JWT; raises `401`.
* **Authorization** dependency (`authorize_workspace_admin`) → coarse role / ownership check; raises `403`.
* Deeper, resource‑state‑dependent authorization belongs in **services** (domain exceptions).

---

## Async Essentials

FastAPI, SQLModel, and SQLAlchemy **all** run in the event‑loop. Follow these rules for predictable non‑blocking behaviour:

1. **Async DB driver** – use `asyncpg` for Postgres, `aiosqlite` for SQLite, etc.
2. **No hidden blocking calls** – wrap legacy sync SDKs in `run_in_threadpool`:

   ```python
   from fastapi.concurrency import run_in_threadpool
   data = await run_in_threadpool(sync_s3_client.get_object, Bucket="demo", Key="file")
   ```
3. **One open session per request** – provided by `get_session`, reused across repos/services.
4. **`async with` everywhere** – engine connects, file I/O, S3 clients, HTTP clients (`httpx.AsyncClient`).
5. **Testing** – use `pytest‑asyncio` fixtures and `asyncio.run`.

---

## 🎯 Dependency Injection & Factories

### Session provider

```python
async_engine = create_async_engine(DB_URL, echo=False, future=True)
async_session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
```

### Factory functions

```python
async def get_user_repo(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

async def get_user_service(repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(repo)
```

### Unit‑of‑Work (optional)

Wrap multiple repos under one `AsyncSession` transaction for atomic operations.

---

## 📋 Best Practices & Gotchas

1. Use an async database driver; blocking SDKs must go in a threadpool.
2. Type‑hint repo returns (`-> Entity | None`) so static checkers force null handling.
3. No service‑to‑service calls—share logic via helpers or a Unit‑of‑Work.
4. Keep the router thin; put all business rules in services.
5. One `BaseDomainError` keeps the global handler tiny.

---

## 🚀 Final Flow & Cheat‑sheet

```text
1  Router             – HTTP + DI
2  Dependencies       – Auth / basic ACL (HTTPException)
3  Service            – Business rules (DomainError)
4  Repository         – Data access (None)
5  Global handler     – DomainError → HTTP
6  Safety‑net handler – 500 JSON
```

| Component  | Raises             | When                        |
| ---------- | ------------------ | --------------------------- |
| Dependency | `HTTPException`    | Auth / basic access failure |
| Service    | Domain exception   | Business violation          |
| Repository | nothing / DB error | Not found → `None`          |
| Handler    | maps to HTTP code  | `NotFoundError` → 404, etc. |

---

✅ **Async‑first common sense**  •  ✅ **Consistent error mapping**  •  ✅ **Statically testable**  •  ✅ **Sleep‑friendly**
